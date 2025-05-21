# TODO and notes

In a real project, this would actually be in a bug/task tracker software (Jira/Asana/etc)

- [x] Complexity analysis: see branch `complexity_analysis`
- Consider the complexity of doing a lot of Dataframe filtering versus making one big loop that processes every logic for each row
- [ ] what are the risks when the data types are being defined when receiving the CSV input?
- Do deeper research on DF filtering (e.g: `df[df['my_column'].notna()]`) for time and space complexity
- Git commits

  - Commits were made very short, in order to be easir to read. In a real project, we would git-squash the commits in the PR, and rebase it on the newest version of the `dev` branch. That way we get a very clean git history
  - Commits in the "middle" of the branch included lots of prints for debugging, in order to ilustrate the development process

- [x] Escape SQL inserts to prevent SQL injection attacks
  - Given this SO answer: https://stackoverflow.com/questions/71604741/sql-sanitize-python
    - Consider moving the responsibility to the part that executes the SQL, and make sure it is always using escaped parameter passing
      - [x] But assuming we can't do that, we should escape the strings before saving to file. Then we assume that the file will be correctly executed with the escaped strings
- [ ] Add validation for all input fields
  - null
  - out of bounds
  - file type
  - Consider File size limits for input
  - unsupported characters
  - character encoding
- [ ] Consider adjusting the project to handle large file sizes (`chunksize`)
- [ ] Add Linter
- [x] When generating running totals over 'itemCount', should this table be ordered in a specific way to make more sense of the running totals?
  - Maybe not, because maybe they wanted the "running totals" to be a sum of itemCounts grouped by product
    - Previous implementation:
      - #running_totals_df['running_total'] = running_totals_df['itemCount'].cumsum()
      - #running_totals_df.to_csv(f'{OUTPUT_FILES_PATH}/running_totals_df.csv', index=False)
- [x] The error logs are CSV's with rows that have a specific error. They were generated with `.copy(deep=True)` to prevent filtering in any DF to not interfere with another. In order to save memory space, we could move up the CSV generation to be made as soon as possible, and then assign `None` to the DF error log variable (since it could be a quite large object)
- [ ] Consider kinds of systems design architecture
  - Consider kinds of deployment
    - AWS S3, queues, Lambdas
      - These input files would come from somewhere, maybe a queue? (files uploaded to S3, and the event and filenames are sent to RabbitMQ)
      - This process looks like something you would want to be ran everyday at a certain time after the other parties had the time to process and submit to you. Since we wouldn't need a service to be listening 24/7, we can use Lambda for file upload
      - The output files can also be stored on S3, and its executing triggered by the end of the previous processing. Saving output files could be very useful in case of bugs, monitoring or even auditing
      - Any exceptions during processing should send an event on an alerting system
- [ ] Consider adding idempotency to the SQL output files (running with the same inputs wouldn't cause duplicate entries on the DB)
