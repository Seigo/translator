# TODO & Notes

> In a real project, these tasks would be tracked in a bug/task tracker (Jira, Asana, etc).

---

## ✅ Completed

- **Complexity analysis:**  
  See branch `complexity_analysis`.

- **Escape SQL inserts to prevent SQL injection attacks:**

  - Reference: [StackOverflow answer](https://stackoverflow.com/questions/71604741/sql-sanitize-python)
  - If possible, use parameterized queries.
  - For this project, escape strings before saving to file.

- **Running totals over `itemCount`:**

  - Considered grouping by product for running totals.
  - Previous implementation:
    ```python
    # running_totals_df['running_total'] = running_totals_df['itemCount'].cumsum()
    # running_totals_df.to_csv(f'{OUTPUT_FILES_PATH}/running_totals_df.csv', index=False)
    ```

- **Error logs:**
  - Error logs are CSVs with rows that have a specific error.
  - Used `.copy(deep=True)` to avoid DataFrame filtering side effects.
  - To save memory, generate CSVs as soon as possible and set error DataFrames to `None` after writing.

---

## 🟡 In Progress / To Consider

### Data Processing & Validation

- [ ] **Data type risks:**  
       What are the risks when the data types are being defined when receiving the CSV input?

- [ ] **Deep dive on DataFrame filtering:**  
       Research time and space complexity of DataFrame filtering (e.g., `df[df['my_column'].notna()]`).

- [ ] **Validation for all input fields:**

  - [ ] Null checks
  - [ ] Out-of-bounds values
  - [ ] File type validation
  - [ ] File size limits
  - [ ] Unsupported characters
  - [ ] Character encoding

- [ ] **Handle large file sizes:**  
       Consider using `chunksize` for processing large CSVs.

### Code Quality & Tooling

- [ ] **Add linter:**  
       Integrate a linter (e.g., flake8, black, pylint) for code quality.

### System Design & Architecture

- [ ] **Consider system design and deployment:**

  - [ ] AWS S3, queues, Lambdas
    - Input files could come from S3, with events sent to a queue (e.g., RabbitMQ).
    - This process could be scheduled (e.g., daily) rather than running as a 24/7 service.
    - Output files can be stored on S3 for auditing and monitoring.
    - Exceptions during processing should trigger alerts.

- [ ] **Idempotency:**  
       Ensure SQL output files are idempotent (running with the same inputs does not cause duplicate DB entries).

---

## 📝 Git Commit Notes

- Commits are intentionally short for readability.
- In a real project, use git-squash and rebase on the latest `dev` branch for a clean history.
- Some commits include debug prints to illustrate the development process.

---
