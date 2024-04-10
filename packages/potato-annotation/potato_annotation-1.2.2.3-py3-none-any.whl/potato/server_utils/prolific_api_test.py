from prolific_apis import *

prolific = ProlificStudy(token = 'yRB91_ngkHclqd36bhXCGWwl5fqU4iVlXX-2i61cfNoh7Tpvh4tH8R6IAxEBsYrkMnyc4X8tEpmmJhHXiHiRkFZYIm_Jr-pCoXFqyrIHX30qUuT5RMcIc7rG',
                         study_id='6498cf2053b6c5b98075f52c', saving_dir='../')
prolific.list_all_studies()
start_time = time.time()
print(prolific.update_submission_status())
end_time = time.time()
execution_time = end_time - start_time
print(execution_time)

prolific = ProlificStudy(token = 'yRB91_ngkHclqd36bhXCGWwl5fqU4iVlXX-2i61cfNoh7Tpvh4tH8R6IAxEBsYrkMnyc4X8tEpmmJhHXiHiRkFZYIm_Jr-pCoXFqyrIHX30qUuT5RMcIc7rG',
                         study_id='651ca114a0a3dc560dd00c2a', saving_dir='../')
prolific.list_all_studies()
start_time = time.time()
print(prolific.update_submission_status())
end_time = time.time()
execution_time = end_time - start_time
print(execution_time)