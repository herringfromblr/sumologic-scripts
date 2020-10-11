# Scripts

This folder contains 1 script so far:
### 1. **sumologic_query.py** 

In order to use that script 2 additional Python modules should be installed:
- sumologic-sdk
- click

You need to install these modules in advance:
> pip install sumologic-sdk<br\>
> pip install click<br\>

Usage:
- Run **--help** command to see avaliable script options 
> python sumologic_query.py --help<br\>
- Run the query:
> python sumologic_query.py -id \<access_id\> -k \<access_key\> -e \<endpoint\> -ft \<from_time\> -tt \<to_time\> **\<query_file\>**

Example:
> python sumologic_query.py -id xxxxxxx -k xxxxxxx -e https://api.us2.sumologic.com/api -ft 2020-10-01T00:00:00 -tt 2020-10-06T11:00:00 query1.sumoql

