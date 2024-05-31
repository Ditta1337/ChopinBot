import matplotlib.pyplot as plt

if __name__ == "__main__":
    x = []
    y = []
    with open("./losses.txt", "r") as f:
        for line in f.readlines():
            new_x, new_y = line[:-2].split(" ")
            x.append(int(new_x))
            y.append(float(new_y))

    print(x, y)

    plt.plot(x, y)
    plt.title("Loss over epochs")
    plt.xlabel("epochs")
    plt.ylabel("loss")
    plt.show()
