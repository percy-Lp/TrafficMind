import cv2


def center(x, y, w, h):
    x1 = int(w/2)
    y1 = int(h/2)
    cx = x + x1
    cy = y + y1
    return cx, cy


def detect_line_count(frame, height, width, result):
    cv2.line(frame, (0, height // 3 * 2), (width, height // 3 * 2), (255, 255, 0), 1)  # 绘制检测线
    # cv2.line(frame, (0, 500), (width, 500), (255, 255, 0))   # TODO get height & width

    carnum1 = 0
    carnum2 = 0
    cars = []
    # 如果没有识别的：
    if result.boxes.id is None:
        labels_write = "暂未识别到目标！"
        return

    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)

        # 对车辆宽高进行判断，验证是否是有效车辆
        isValid = (w >= 90) and (h >= 90)
        if (not isValid):
            continue
        # 如果是有效车辆，则绘制边框
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cpoint = center(x, y, w, h)  # 计算汽车中心点
        cars.append(cpoint)
        cv2.circle(frame, (cpoint), 5, (0, 0, 255), -1)
        for (x, y) in cars:  # 遍历数组，如果车的中心点落在检测线的有效区域内，则计数+1，然后去除该数组
            print(y, 544, 556)
            if ((y > 544) and (y < 556)) and (x < 605):
                carnum1 += 1
                cars.remove((x, y))
                print(carnum1)
            if ((y > 544) and (y < 556)) and (x > 605):
                carnum2 += 1
                cars.remove((x, y))
                print(carnum2)
    # text_lines = ["cars_in:" + str(carnum1), "cars_out:" + str(carnum2)]
    return carnum1, carnum2


