import csv
import time
import serial

PORT = "COM5"
BAUD = 115200

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    filename = f"csi_record_{int(time.time())}.csv"

    print(f"Recording CSI data to: {filename}")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if line and line[0].isdigit():
                row = line.split(",")
                writer.writerow(row)
                print(line)

if __name__ == "__main__":
    main()
