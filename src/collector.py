r""" HH job vacancies data collector

!WIP

--------------------------------------------------------------------------------
MIT License

Copyright (c) 2022 Mike Kazantsev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

--------------------------------------------------------------------------------

"""

# modules import
import hashlib
import os
import pickle
import re

from datetime import timedelta as td, datetime, date

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from tqdm import tqdm

import pandas as pd

class Collector:
    
    # class constants
    # API base url address
    __API_BASE_URL = "https://api.hh.ru/vacancies/"
    
    # API request limit
    __API_HOURLY_LIMIT = 3000

    # cache folder 
    __CACHE_DIR = "../cache/"

    # column names for the returned table
    __DICT_KEYS = (
        "vacancy_id",
        "vacancy_name",
        "area_name",
        "employer_id",
        "employer_name",
        "employer_alternate_url",
        "salary_from",
        "salary_to",
        "salary_currency",
        "experience_name",
        "schedule_name",
        "employment_name",
        "key_skills",
        "specializations",
        "professional_roles",
        "published_at",
        "created_at",
        "initial_created_at",
        "alternate_url",
        "description",
        "responses",
        "retrieve_date",
    )
    
    def __init(self):
        # TODO:
        # Add loading config and last run time for the api counter
        self._api_counter = 0
    
    @staticmethod
    def clean_tags(html_text: str) -> str:
        """Removing HTML tags from the string
        Parameters
        ----------
        html_text: str
            Input string with tags
        Returns
        -------
        result: string
            Clean text without HTML tags
        """
        pattern = re.compile("<.*?>")
        return re.sub(pattern, "", html_text)
    
    def get_vacancy(self, vacancy_id: str, resps: int):
        """Getting vacancy data for ID
        
        Parameters
        ----------
        vacancy_id : str
            Vacancy ID
        resps : int
            Number of responses        
        Returns fields (in order):
        --------------------------
        vacancy_id
        ["name"]
        ["area"]["name"]
        ["employer"]["id"]
        ["employer"]["name"]
        ["employer"]["alternate_url"]
        ["salary"]["from"]
        ["salary"]["to"]
        ["salary"]["currency"]
        ["experience"]["name"]
        ["schedule"]["name"]
        ["employment"]["name"]
        list of ["key_skills"]["id"]["name"]
        list of ["specializations"]["id"]["name"]
        list of ["professional_roles"]["id"]["name"]
        ["published_at"]
        ["created_at"]
        ["initial_created_at"]
        ["alternate_url"]
        ["description"]
        "responses" - taken from an argument
        "retrieve_date" - current date
        """
        url = f"{self.__API_BASE_URL}{vacancy_id}"
        try:
            vacancy = requests.api.get(url).json()
        except:
            return (
                vacancy_id,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            )
        # Checking salary as it can be null
        salary = vacancy.get("salary")
        salary_data = {"from": None, "to": None, "currency": None}
        if salary is not None:
            salary_data["from"] = salary["from"]
            salary_data["to"] = salary["to"]
            salary_data["currency"] = salary["currency"]
        # Checking employer for None
        employer = vacancy.get("employer")
        employer_data = {"id": None, "name": None, "alternate_url": None}
        if employer is not None:
            employer_data["id"] = employer.get("id")
            employer_data["name"] = employer.get("name")
            employer_data["alternate_url"] = employer.get("alternate_url")
        key_skills = vacancy.get("key_skills")
        if key_skills is not None:
            key_skills_data = [item["name"] for item in key_skills]
        else:
            key_skills_data = []
        specializations = vacancy.get("specializations")
        if specializations is not None:
            specializations_data = [item["name"] for item in specializations]
        else:
            specializations_data = []
        professional_roles = vacancy.get("professional_roles")
        if professional_roles is not None:
            professional_roles_data = [item["name"] for item in professional_roles]
        else:
            professional_roles_data = []
        # Create pages tuple
        return (
            vacancy_id,
            vacancy.get("name"),
            vacancy.get('area', {}).get('name'),
            employer_data["id"],
            employer_data["name"],
            employer_data["alternate_url"],
            salary_data["from"],
            salary_data["to"],
            salary_data["currency"],
            vacancy.get('experience', {}).get('name'),
            vacancy.get('schedule', {}).get('name'),
            vacancy.get('employment', {}).get('name'),
            key_skills_data,
            specializations_data,
            professional_roles_data,
            vacancy.get("published_at"),
            vacancy.get("created_at"),
            vacancy.get("initial_created_at"),
            vacancy.get("alternate_url"),
            clean_tags(str(vacancy.get("description") or "")),
            resps,
            date.today().isoformat()
        )

    
    def collect_vacancies(query: Optional[Dict],
                      existing_ids: Optional[List],
                      refresh: bool = False,
                      responses: bool = False,
                      progress_info: bool = True,
                      max_workers: int = 1) -> Dict:
        """Collect and parse the vacancy JSONs for the query
        Parameters
        ----------
        query : dict
            Search query params for GET requests.
        existing_ids : list
            List with existing vacancy ids (taken either for the same date beforehand or the whole dataset)
        refresh :  bool
            Refresh cached data
        responses : bool
            Whether to collect the number of vacancy responses or not
        max_workers :  int
            Number of workers for threading.
        Returns
        -------
        dict
            Dict of useful data from vacancies
        """

        # Get cached data if exists...
        cache_name: str = urlencode(query)
        cache_hash = hashlib.md5(cache_name.encode()).hexdigest()
        cache_file = os.path.join(self.__CACHE_DIR, cache_hash)
        result = {}

        try:
            if not refresh:
                if progress_info:
                    print(f"[INFO]: Geting results from cache! Enable refresh option to update results.")
                return pickle.load(open(cache_file, "rb"))
        except (FileNotFoundError, pickle.UnpicklingError):
            pass

        if existing_ids is None:
            existing_ids = []   

        if responses:
            query['responses_count_enabled'] = True

        # Customize HTTPAdapter and Retry Strategy
        retry_strategy = Retry(
            total=10,
            status_forcelist=[413, 429, 503],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        target_url = self.__API_BASE_URL + "?" + urlencode(query)
        num_pages = http.get(target_url).json().get("pages")
        if num_pages is None:
            return result, 1

        # Collect vacancy IDs...
        ids = []
        resps = []

        for idx in range(num_pages + 1):
            response = requests.get(target_url, {"page": idx})
            self._api_counter +=1
            data = response.json()
            if "items" not in data:
                break
            ids.extend(x["id"] for x in data["items"])
            resps.extend(x.get('counters', {}).get('responses') for x in data["items"])

        ids = list(set(ids) - set(existing_ids))

        # Collect vacancies...
        jobs_list = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            if progress_info:
                for vacancy in tqdm(
                    executor.map(get_vacancy, ids, resps),
                    desc="Get data via HH API",
                    ncols=100,
                    total=len(ids),
                ):
                    jobs_list.append(vacancy)
                    self._api_counter+=1
            else:
                for vacancy in executor.map(get_vacancy, ids, resps):
                    jobs_list.append(vacancy)
                    self._api_counter+=1

        unzipped_list = list(zip(*jobs_list))

        if len(unzipped_list) > 0:
            for idx, key in enumerate(__DICT_KEYS):
                result[key] = unzipped_list[idx]
            pickle.dump(result, open(cache_file, "wb"))

        return result
    
    def retrieve_queries(query_texts, query_date, refresh = True, progress_info = True):
        """
        Retrieve data for the list of queries for the certain date.    
        Data is saved to f"../data/download/{query_date}_{query_texts[query_id]}.csv" as CSV files.
        Parameters
        ----------
        query_texts : list
            List of strings with the search query request
        query_date : string
            Date string in ISO 8601 format (YYYY-MM-DD)
        Returns
        -------
        bool
            True if all the data retrieved, False if API limit reached
        """
        # TODO: add counter reset, and pause depending on the last download time?
        
        # local counters
        downloaded_counter = 0
        dropped_counter = 0        
        # distribute vacancies by hour to avoid the 2k API limit
        timelist = pd.to_datetime(pd.date_range(start = query_date,
                                 periods=25,
                                 freq = "H")).strftime('%Y-%m-%dT%H:%M:%S').to_list()
        # iterate through texts and every hour of the day 
        for query_id in range (0, len(query_texts)):
            print(f"Downloading for query '{query_texts[query_id]}' for {query_date}")
            try:
                vacancies_df = pd.read_csv(f"../data/download/{query_date}_{query_texts[query_id]}.csv", dtype={
                    'vacancy_id': str,
                    'employer_id': str,
                })
            except:
                vacancies_df = None
            if (vacancies_df is not None):
                if not refresh:
                    continue
                existing_ids = vacancies_df['vacancy_id'].to_list()
            else:
                existing_ids = []
            vacancies_data = []
            for i in range(1, 25):
                temp_data = collect_vacancies(
                        query={"text": query_texts[query_id],
                               "per_page": 50,
                               "date_from": timelist[i-1],
                               "date_to": timelist[i],
                              },
                        existing_ids=existing_ids,
                        responses=True,
                        refresh=refresh,
                        progress_info=progress_info,
                    )
                vacancies_data.append(pd.DataFrame(temp_data[0]))
                downloaded_counter += temp_data[1]
                self._api_counter += temp_data[1]
                if self._api_counter >= self.__API_HOURLY_LIMIT:
                    break
            # combine daily data into the dataframe, remove duplicates and ave it
            vacancies_df_new = pd.concat(vacancies_data)
            vacancies_df = pd.concat([vacancies_df, vacancies_df_new])
            if vacancies_df.shape[0] == 0:
                continue
            dropped_counter += vacancies_df['vacancy_name'].isnull().sum()
            vacancies_df = vacancies_df[vacancies_df['vacancy_name'].notnull()]
            vacancies_df = vacancies_df.drop_duplicates(subset='vacancy_id')
            vacancies_df['query'] = query_texts[query_id]
            vacancies_df.to_csv(f"../data/download/{query_date}_{query_texts[query_id]}.csv",index=False)
            if self._api_counter >= self.__API_HOURLY_LIMIT:
                print(f"API download limit reached, downloaded {downloaded_counter} vacancies for {query_date}")
                return False
        print(f"Downloaded all {downloaded_counter} vacancies for {query_date}")
        if dropped_counter > 0:
            print(f"Removed nulls: {dropped_counter}")
        return True