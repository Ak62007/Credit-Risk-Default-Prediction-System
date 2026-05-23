## Everthing I know about the data

### day-1
This dataset contains the full LendingClub data available from their site. There are separate files for accepted and rejected loans. The accepted loans also include the FICO scores, which can only be downloaded when you are signed in to LendingClub and download the data.

- from what i have seen the data is about loans. The is the loans data from leadingclub.
- from what i see there are two .csv files one for accepted loans and one for rejected loans.
- both are of around 1.5 gb
- both i think has data from 2007 -> 2018.

#### Known Issues / Caveats
Some columns likely contain post-default information (e.g. payments made, recoveries) that would not be available at loan origination time. These must be identified and excluded during feature engineering to prevent leakage.

### day-2
Started doing some EDA(on the accepted loans):
- data has 151 columns and 2260701 rows
- I checked the loan status column which just tells the current status of the loans, This will be our label.
- This columns takes multiple values. I made some decisions while label creation. Those are as followings:
    1. 'Current', 'In Grace Period', 'Late (16-30 days)' has been dropped.
    2. 'Fully Paid' and 'Does not meet the credit policy. Status:Fully Paid' are set to 0 else are 1.
    3. Class Distribution: 0 -> 78.765025 %, 1 -> 21.234975 %