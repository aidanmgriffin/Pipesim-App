import csv
import os

def process_csv(filename):

    print("invalid") 

    with open(filename, newline = '') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            print(row)

    output_file = 'output_now.csv'
    with open(os.path.join('output', output_file), 'w') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow("output")

    return output_file



        

