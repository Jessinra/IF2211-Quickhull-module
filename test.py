import numpy as np
import pandas as pd
import matplotlib.pyplot


def generate_points(count):
    """
    Generate random points (x,y)
    :param count: amount of point
    :type count: int
    :return: List of randomized point
    :rtype: DataFrame
    """

    x_min = 0
    x_max = 100
    y_min = 0
    y_max = 100

    x_list = np.random.randint(x_min, x_max, size=count)
    y_list = np.random.randint(y_min, y_max, size=count)

    point_list = pd.DataFrame({'x': x_list, 'y': y_list})

    return point_list


def check_cond(point_1, point_2, check_point):
    """
    Check a point position based on a line created by 2 points (left / right / mid)
    :param point_1: line first point
    :type point_1: DataFrame element
    :param point_2: line second point
    :type point_2: DataFrame element
    :param check_point: point which is going to be checked
    :type check_point: DataFrame element
    :return: point position
    :rtype: string
    """

    try:
        p1_x, p1_y, p1_c = point_1
    except:
        p1_x, p1_y = point_1

    try:
        p2_x, p2_y, p2_c = point_2
    except:
        p2_x, p2_y = point_2

    try:
        pc_x, pc_y, pc_c = check_point
    except:
        pc_x, pc_y = check_point

    # Use determinant to determine position
    det = (p2_x - p1_x) * (pc_y - p1_y) - (p2_y - p1_y) * (pc_x - p1_x)

    if det > 0:
        return "left"
    elif det < 0:
        return "right"
    else:
        return "mid"


def filter_left_right(left_most, right_most, point_list):
    """
    Get all left/right condition
    :param left_most: line left most point (end)
    :type left_most: DataFrame element
    :param right_most: line right most point (end)
    :type right_most: DataFrame element
    :param point_list: list of points
    :type point_list: DataFrame
    :return: list of points on line left and right
    :rtype: DataFrame
    """

    # Create an empty list for handle point position
    temp = np.empty(point_list.index[-1] + 1, dtype='U8')

    # Check every point position
    for index, row in point_list.iterrows():
        temp[index] = check_cond(left_most, right_most, row)

    # Filter out None in list
    temp = temp[temp != ''].copy()

    # Add a column of condition (left / right)
    point_list['cond'] = temp

    # Return copy of masked data frame
    line_right = point_list.loc[point_list['cond'] == 'right'].copy()
    line_left = point_list.loc[point_list['cond'] == 'left'].copy()

    return line_left, line_right


def left_most_point(point_list):
    """
    Get the left most point
    :param point_list: list of point
    :type point_list: DataFrame
    :return: left most point
    :rtype: DataFrame element
    """
    return point_list.loc[point_list['x'].idxmin()]


def right_most_point(point_list):
    """
    Get the right most point
    :param point_list: list of point
    :type point_list: DataFrame
    :return: right most point
    :rtype: DataFrame element
    """
    return point_list.loc[point_list['x'].idxmax()]


def get_furthest_point(line_left, line_right, point_list):
    """
    Get furthest point
    :param line_left: line left point
    :type line_left: DataFrame element
    :param line_right: line right point
    :type line_right: DataFrame element
    :param point_list: list of point to check
    :type point_list: DataFrame
    :return: furthest point
    :rtype: DataFrame element
    """

    def distance(line_left, line_right, point):
        """
        Get distance from a point to the line created by 2 points
        :param line_left: line left point
        :type line_left: DataFrame element
        :param line_right: line right point
        :type line_right: DataFrame element
        :param point: point to check
        :type point: DataFrame element
        :return: distance
        :rtype: float
        """

        try:
            x0, y0, c0 = point
        except:
            x0, y0 = point

        try:
            x1, y1, c1 = line_left
        except:
            x1, y1 = line_left

        try:
            x2, y2, c2 = line_right
        except:
            x2, y2 = line_right

        # Calculate distance
        top_eq = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        bot_eq = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5

        return top_eq / bot_eq

    furthest_point = None
    max_distance = 0

    # Find the furthest
    for index, point in point_list.iterrows():
        point_distance = distance(line_left, line_right, point)
        if point_distance > max_distance:
            max_distance = point_distance
            furthest_point = point

    return furthest_point


def quick_hull(line_left, line_right, point_list):
    """
    Algorithm to find the most outer line of a clustered points
    :param line_left: line left edge
    :type line_left: DataFrame element
    :param line_right: line right edge
    :type line_right: DataFrame element
    :param point_list: list of point to check
    :type point_list: DataFrame
    :return: ines connecting the outer points
    :rtype: list
    """

    # If there's no more point to check (basis)
    if len(point_list['x']) == 0:
        return [(line_left, line_right)]

    # Get furthest point from line
    furthest_point = get_furthest_point(line_left, line_right, point_list)

    # Divide point into LEFT-line's left / right
    point_on_line_left, point_on_line_right = filter_left_right(line_left, furthest_point, point_list)

    # Delete side that's useless
    delete_side = check_cond(line_left, furthest_point, line_right)

    # Choose one side that's outer
    rec_point_list = None
    if delete_side == "right":
        rec_point_list = point_on_line_left
    elif delete_side == "left":
        rec_point_list = point_on_line_right

    # Recurse
    outer_line_left = quick_hull(line_left, furthest_point, rec_point_list)

    # Divide point into RIGHT-line's left / right
    point_on_line_left, point_on_line_right = filter_left_right(furthest_point, line_right, point_list)

    # Delete side that's useless
    delete_side = check_cond(furthest_point, line_right, line_left)

    # Choose one side that's outer
    rec_point_list = None
    if delete_side == "right":
        rec_point_list = point_on_line_left
    elif delete_side == "left":
        rec_point_list = point_on_line_right

    # Recurse
    outer_line_right = quick_hull(furthest_point, line_right, rec_point_list)

    return outer_line_left + outer_line_right


def show_output(tuple_list):
    """
    Format output so it's easier to read
    :param tuple_list: list of tuple indicate line
    :type tuple_list: list
    """

    final = []
    for point_1, point_2 in tuple_list:
        line = ((point_1['x'], point_1['y']), (point_2['x'], point_2['y']))
        final.append(line)

    print("========================================")
    print("======          OUTER LINE          ====")
    print("========================================")
    for item in final:
        print(item)


def draw(point_list, tuple_list):
    """
    Display visualization
    :param point_list: list of point at start
    :type point_list: DataFrame
    :param tuple_list: list of tuples indicating line
    :type tuple_list: List
    """

    # Setup
    fig = matplotlib.pyplot.figure(1)
    fig.canvas.set_window_title('13516112')
    canvas = fig.add_subplot(111, facecolor='#232e33')
    fig.canvas.draw()

    # Create init scatter
    x = point_list['x']
    y = point_list['y']
    canvas.scatter(x, y, color="#759ad6")

    # Parse line tuple
    final_x = []
    final_y = []
    for point_1, point_2 in tuple_list:
        # Append line edge to list
        final_x.append(point_1['x'])
        final_x.append(point_2['x'])
        final_y.append(point_1['y'])
        final_y.append(point_2['y'])

        # Create line
        list_x = [point_1['x'], point_2['x']]
        list_y = [point_1['y'], point_2['y']]
        canvas.plot(list_x, list_y, color="#ffa632")

    # Create line edge scatter
    canvas.scatter(final_x, final_y, color="#ffa632")

    # Draw it !
    matplotlib.pyplot.show()


if __name__ == '__main__':

    # Initialize point
    point_count = 25
    point_list = generate_points(point_count)

    # Find the left and right most
    left_most = left_most_point(point_list)
    right_most = right_most_point(point_list)

    # Separate the rest of point into two
    point_on_line_left, point_on_line_right = filter_left_right(left_most, right_most, point_list)

    # Apply quick hull algorithm
    outer_line_left = quick_hull(left_most, right_most, point_on_line_left)
    outer_line_right = quick_hull(left_most, right_most, point_on_line_right)
    outer_final = outer_line_left + outer_line_right

    # Display output
    show_output(outer_final)
    draw(point_list, outer_final)
