## Everthing I know about the data

### day-1
This dataset contains the full LendingClub data available from their site. There are separate files for accepted and rejected loans. The accepted loans also include the FICO scores, which can only be downloaded when you are signed in to LendingClub and download the data.

- from what i have seen the data is about loans. The is the loans data from leadingclub.
- from what i see there are two .csv files one for accepted loans and one for rejected loans.
- both are of around 1.5 gb
- both i think has data from 2007 -> 2018.

#### Known Issues / Caveats
Some columns likely contain post-default information (e.g. payments made, recoveries) that would not be available at loan origination time. These must be identified and excluded during feature engineering to prevent leakage.