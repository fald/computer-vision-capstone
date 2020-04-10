import numpy as np
import cv2

# TODO: Account for 50p
# TODO: Do it for CAN

def get_img(filename):
    # Read image with cv2, but color information is probably too much, so grayscale is fine.
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    # Blur coins; circle detection with too crisp an image will detect circles freaking everywhere. Ease up, buckaroo.
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Original image, so circles are drawn on the color image, just to be shown back to user
    orig_img = cv2.imread(filename)

    return img, orig_img


def get_circles(img):
    # Hough transform. Read up on the documentation for details, but looks like it just works, which is enough for now (it is not)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 0.9, 120, param1=50, param2=27, minRadius=60, maxRadius=120)

    # Convert numbers to unsigned short integers so they can be drawn back on in the right pixel locations.
    circles = np.uint16(np.round(circles))

    return circles


def get_radii(circles):
    return [circle[2] for circle in circles[0]]


def av_pix(img, circles, size):
    # What?
    # Average brightness, basing the coin determination on that alone.
    # Take a square of size, within the circle, to find av bright within. Very...hm. Will it work? Is it garbage?
    # I freaking love list comprehensions.
    av_value = [np.mean(img[coords[1]-size:coords[1] + size, coords[0] - size:coords[0] + size]) for coords in circles[0]]
    # for coords in circles[0, :]:
    #     # Use a slice from -size -> +size on x, y coords from radius
    #     col = np.mean(img[coords[1]-size:coords[1] + size, coords[0] - size:coords[0] + size])
    #     av_value.append(col)
    return av_value


def est_values(img, circles, size=20):
    # Not sophisticated at all!
    values = []
    bright_value = av_pix(img, circles, size)
    radii = get_radii(circles)
    print(bright_value, radii)
    for b, r in zip(bright_value, radii):
        if b > 150:
            if r > 90:
                values.append(10)
            else:
                values.append(5)
        else:
            if r > 90:
                values.append(2)
            else:
                values.append(1)
    return values


def draw_circles(circles, orig_img, values):
    for count, circle in enumerate(circles[0], 1):
        # Heh, because of draw order of circles then labels, some circles overlap. Good times.
        # Draw the circle.
        cv2.circle(orig_img, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
        # Draw the center dot...for reasons.
        cv2.circle(orig_img, (circle[0], circle[1]), 2, (255, 0, 0), 3)
        # Label 'em
        # cv2.putText(orig_img, f'coin {count}', (circle[0], circle[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
        cv2.putText(orig_img, f'{values[count - 1]}p', (circle[0], circle[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
    cv2.putText(orig_img, f'Estimated total: {np.sum(values)}p', (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 0, 0), 2)


if __name__ == "__main__":

    img, orig_img = get_img("capstone_coins.png")
    circles = get_circles(img)

    values = est_values(img, circles)

    draw_circles(circles, orig_img, values)

    cv2.imshow("Detected Coins", orig_img)
    # cv2.imshow("Detected Coins", img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
