from deepdiff.diff import DeepDiff
from concurrent.futures.process import ProcessPoolExecutor
import concurrent

t1 = [[1, 2, 3, 9], [9, 8, 5, 9]]
t2 = [[1, 2, 4, 10], [4, 2, 5]]

futures = []


if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=1) as executor:
        results = executor.map(DeepDiff, t1, t2)
        for result in results:
            print(result)
        # futures.append(executor.submit(DeepDiff, t1, t2))
        
    #     for future in concurrent.futures.as_completed(futures, timeout=10):
    #         print(future._exception)
    #         print(future._result)
    # with futures.ProcessPoolExecutor(2) as e:
    #         print(_)
