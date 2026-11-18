import importlib
import os
import asyncio
import inspect
from functools import partial

async def check_email(email):
    results = {}

    sites_path = os.path.join(os.path.dirname(__file__), "sites")
    tasks_info = []
    print("[DEBUG] Looking for sites in:", sites_path)
    print("[DEBUG] Found entries:", os.listdir(sites_path))

    for site in os.listdir(sites_path):
        site_path = os.path.join(sites_path, site)
        if os.path.isdir(site_path):
            script_path = os.path.join(site_path, f"{site}.py")
            if os.path.exists(script_path):
                module_name = f"mail.sites.{site}.{site}"
                try:
                    module = importlib.import_module(module_name)
                    func_name = f"check_{site}_email"
                    if hasattr(module, func_name):
                        check_function = getattr(module, func_name)

                        # Store info to generate tasks repeatedly
                        tasks_info.append((site, check_function))

                except Exception as e:
                    print(f"[IMPORT ERROR in {module_name}]", e)
                    results[site.capitalize()] = False


    # Run the checks 10 times and OR the results
    final_results = {}
    for _ in range(2):
        tasks = []

        for site, check_function in tasks_info:
            async def run_check(site_name=site, func=check_function):
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(email)
                    else:
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, partial(func, email))
                    return (site_name.capitalize(), bool(result))
                except Exception:
                    return (site_name.capitalize(), False)

            tasks.append(run_check())

        check_results = await asyncio.gather(*tasks)
        for site, result in check_results:
            final_results[site] = final_results.get(site, False) or result

    print("[DEBUG] Final results:", final_results)
    return final_results
