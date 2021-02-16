from selenium.common.exceptions import WebDriverException

def any_of(*expected_conditions):
    """ An expectation that any of multiple expected conditions is true.
    Equivalent to a logical 'OR'.
    Returns results of the first matching condition, or False if none do. """
    def any_of_condition(driver):
        for expected_condition in expected_conditions:
            try:
                result = expected_condition(driver)
                if result:
                    return result
            except WebDriverException:
                pass
        return False
    return any_of_condition


def all_of(*expected_conditions):
    """ An expectation that all of multiple expected conditions is true.
    Equivalent to a logical 'AND'.
    Returns: When any ExpectedCondition is not met: False.
    When all ExpectedConditions are met: A List with each ExpectedCondition's return value. """
    def all_of_condition(driver):
        results = []
        for expected_condition in expected_conditions:
            try:
                result = expected_condition(driver)
                if not result:
                    return False
                results.append(result)
            except WebDriverException:
                return False
        return results
    return all_of_condition


def none_of(*expected_conditions):
    """ An expectation that none of 1 or multiple expected conditions is true.
    Equivalent to a logical 'NOT-OR'.
    Returns a Boolean """
    def none_of_condition(driver):
        for expected_condition in expected_conditions:
            try:
                result = expected_condition(driver)
                if result:
                    return False
            except WebDriverException:
                pass
        return True
    return none_of_condition