from pandas import DataFrame
from FancySchmancyTestsplit.fst import fancy_schmancy_testsplit
# src\FancySchmancyTestsplit\__init__.py has to have import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__))) for import to work

def test_fst():
    df = DataFrame(data= {"Column A":[10, 14, 12, 13, 9, 5, 13, 16, 18, 4, 12],
        "Column B": ["Cat1", "Cat1", "Cat2", "Cat2", "Cat2", "Cat2", "Cat2", "Cat2", "Cat2", "Cat2", "Cat2"]})

    X_train, X_test, y_train, y_test = \
    fancy_schmancy_testsplit(
        data = df,
        label_column= "Column B",
        test_split= 0.5,
        seed= 42
    )

    df1 = y_train[y_train["Column B"] == "Cat1"][["Column B", "Column B"]]
    assert df1.shape[0] == 1

    df2 = X_train[y_train["Column B"] == "Cat1"][["Column A", "Column A"]]
    assert df2.shape[0] == 1

    df3 = y_test[y_test["Column B"] == "Cat1"][["Column B", "Column B"]]
    assert df3.shape[0] == 1

    df4 = X_test[y_test["Column B"] == "Cat1"][["Column A", "Column A"]]
    assert df4.shape[0] == 1

    print("all tests passed")

    pass

test_fst()