r"""
                                                             
  _____/ ____\______ ________________    ____   ___________ 
 /  _ \   __\/  ___// ___\_  __ \__  \  /  _ \_/ __ \_  __ \
(  <_> )  |  \___ \\  \___|  | \// __ \(  <_> )  ___/|  | \/
 \____/|__| /____  >\___  >__|  (____  /\____/ \___  >__|   
                 \/     \/           \/            \/         
"""

import asyncio
import contextvars
import logging
import math
import traceback

import arrow
from tenacity import (
    AsyncRetrying,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_random,
)

import ofscraper.utils.args.read as read_args
import ofscraper.utils.cache as cache
import ofscraper.utils.constants as constants
import ofscraper.utils.progress as progress_utils
from ofscraper.classes.semaphoreDelayed import semaphoreDelayed
from ofscraper.utils.context.run_async import run

log = logging.getLogger("shared")
attempt = contextvars.ContextVar("attempt")
sem = None


@run
async def get_pinned_posts_progress(model_id, c=None):
    tasks = []
    job_progress = progress_utils.pinned_progress

    # async with sessionbuilder.sessionBuilder(
    #     limit=constants.getattr("API_MAX_CONNECTION")
    # ) as c:
    tasks.append(
        asyncio.create_task(
            scrape_pinned_posts(
                c,
                model_id,
                job_progress=job_progress,
                timestamp=(
                    read_args.retriveArgs().after.float_timestamp
                    if read_args.retriveArgs().after
                    else None
                ),
            )
        )
    )
    data = await process_tasks(tasks, model_id)
    progress_utils.pinned_layout.visible = False
    return data


@run
async def get_pinned_posts(model_id, c=None):
    tasks = []
    with progress_utils.set_up_api_pinned():

        tasks.append(
            asyncio.create_task(
                scrape_pinned_posts(
                    c,
                    model_id,
                    job_progress=progress_utils.pinned_progress,
                    timestamp=(
                        read_args.retriveArgs().after.float_timestamp
                        if read_args.retriveArgs().after
                        else None
                    ),
                )
            )
        )
    return await process_tasks(tasks, model_id)


async def process_tasks(tasks, model_id):
    responseArray = []
    page_count = 0
    overall_progress = progress_utils.overall_progress

    page_task = overall_progress.add_task(
        f"Pinned Content Pages Progress: {page_count}", visible=True
    )
    while bool(tasks):
        new_tasks = []
        try:
            async with asyncio.timeout(
                constants.getattr("API_TIMEOUT_PER_TASKS") * max(len(tasks), 2)
            ):
                for task in asyncio.as_completed(tasks):
                    try:
                        result, new_tasks_batch = await task
                        new_tasks.extend(new_tasks_batch)
                        page_count = page_count + 1
                        overall_progress.update(
                            page_task,
                            description=f"Pinned Content Pages Progress: {page_count}",
                        )
                        responseArray.extend(result)
                    except Exception as E:
                        log.traceback_(E)
                        log.traceback_(traceback.format_exc())
                        continue
        except TimeoutError as E:
            log.traceback_(E)
            log.traceback_(traceback.format_exc())
        tasks = new_tasks
    overall_progress.remove_task(page_task)
    log.debug(f"[bold]Pinned Count with Dupes[/bold] {len(responseArray)} found")
    log.trace(
        "pinned raw duped {posts}".format(
            posts="\n\n".join(
                list(map(lambda x: f"dupedinfo pinned: {str(x)}", responseArray))
            )
        )
    )
    seen = set()
    new_posts = [
        post
        for post in responseArray
        if post["id"] not in seen and not seen.add(post["id"])
    ]

    log.trace(f"pinned postids{list(map(lambda x:x.get('id'),new_posts))}")
    log.trace(
        "pinned raw unduped {posts}".format(
            posts="\n\n".join(
                list(map(lambda x: f"undupedinfo pinned: {str(x)}", new_posts))
            )
        )
    )
    log.debug(f"[bold]Pinned Count without Dupes[/bold] {len(new_posts)} found")
    set_check(new_posts, model_id)
    return new_posts


def set_check(unduped, model_id):
    if not read_args.retriveArgs().after:
        seen = set()
        all_posts = [
            post
            for post in cache.get(f"pinned_check_{model_id}", default=[]) + unduped
            if post["id"] not in seen and not seen.add(post["id"])
        ]
        cache.set(
            f"pinned_check_{model_id}",
            all_posts,
            expire=constants.getattr("DAY_SECONDS"),
        )
        cache.close()


async def scrape_pinned_posts(
    c, model_id, job_progress=None, timestamp=None, count=0
) -> list:
    global sem
    sem = semaphoreDelayed(constants.getattr("AlT_SEM"))
    posts = None
    attempt.set(0)

    if timestamp and (
        float(timestamp)
        > (read_args.retriveArgs().before or arrow.now()).float_timestamp
    ):
        return []
    url = constants.getattr("timelinePinnedEP").format(model_id, count)
    log.debug(url)

    async for _ in AsyncRetrying(
        retry=retry_if_not_exception_type(KeyboardInterrupt),
        stop=stop_after_attempt(constants.getattr("NUM_TRIES")),
        wait=wait_random(
            min=constants.getattr("OF_MIN"),
            max=constants.getattr("OF_MAX"),
        ),
        reraise=True,
    ):
        with _:
            new_tasks = []
            await sem.acquire()
            await asyncio.sleep(1)
            try:
                attempt.set(attempt.get(0) + 1)
                task = (
                    job_progress.add_task(
                        f"Attempt {attempt.get()}/{constants.getattr('NUM_TRIES')}: Timestamp -> {arrow.get(math.trunc(float(timestamp))).format(constants.getattr('API_DATE_FORMAT')) if timestamp!=None  else 'initial'}",
                        visible=True,
                    )
                    if job_progress
                    else None
                )
                async with c.requests(url=url)() as r:
                    if r.ok:
                        posts = (await r.json_())["list"]
                        posts = list(
                            sorted(posts, key=lambda x: float(x["postedAtPrecise"]))
                        )
                        posts = list(
                            filter(
                                lambda x: float(x["postedAtPrecise"])
                                > float(timestamp or 0),
                                posts,
                            )
                        )
                        log_id = f"timestamp:{arrow.get(math.trunc(float(timestamp))).format(constants.getattr('API_DATE_FORMAT')) if timestamp!=None  else 'initial'}"
                        if not posts:
                            posts = []
                        if len(posts) == 0:
                            log.debug(f"{log_id} -> number of pinned post found 0")
                        else:
                            log.debug(
                                f"{log_id} -> number of pinned post found {len(posts)}"
                            )
                            log.debug(
                                f"{log_id} -> first date {posts[0].get('createdAt') or posts[0].get('postedAt')}"
                            )
                            log.debug(
                                f"{log_id} -> last date {posts[-1].get('createdAt') or posts[-1].get('postedAt')}"
                            )
                            log.debug(
                                f"{log_id} -> found pinned post IDs {list(map(lambda x:x.get('id'),posts))}"
                            )
                            log.trace(
                                "{log_id} -> pinned raw {posts}".format(
                                    log_id=log_id,
                                    posts="\n\n".join(
                                        list(
                                            map(
                                                lambda x: f"scrapeinfo pinned: {str(x)}",
                                                posts,
                                            )
                                        )
                                    ),
                                )
                            )
                            new_tasks.append(
                                asyncio.create_task(
                                    scrape_pinned_posts(
                                        c,
                                        model_id,
                                        job_progress=job_progress,
                                        timestamp=posts[-1]["postedAtPrecise"],
                                        count=count + len(posts),
                                    )
                                )
                            )
                    else:
                        log.debug(f"[bold]t response status code:[/bold]{r.status}")
                        log.debug(f"[bold]pinned response:[/bold] {await r.text_()}")
                        log.debug(f"[bold]pinned headers:[/bold] {r.headers}")
                        r.raise_for_status()
            except Exception as E:
                await asyncio.sleep(1)
                log.traceback_(E)
                log.traceback_(traceback.format_exc())
                raise E

            finally:
                sem.release()
                job_progress.remove_task(task) if job_progress and task else None
            return posts, new_tasks
