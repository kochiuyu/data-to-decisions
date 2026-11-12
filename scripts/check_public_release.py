from check_retail_release import validate
import sys
if __name__ == '__main__':
    validate('--execute' in sys.argv)
    from check_course_bridges import check
    check('--execute' in sys.argv)
    from check_math_titles import check as check_math_titles
    check_math_titles()
