#!/usr/bin/python

"""
    for parsing SP500 data and drawing a chart
    started Jan 2019
"""

# goal: to draw candlestick charts
# 1 "candle" for each year
# green for higher high and higher low
# red for lower high and lower low
# brown for higher high and lower low -- with arrows, going toward more recent
# grey for lower high and higher lower
# Note: Since the market is closed on 1/1, we count the previous open day for
# the first day of each year.

import sys, string, csv, datetime, operator
from sys import stderr
import matplotlib.pyplot as plt

allRows = []
daysClose = {} #dictionary of day to closing amount
daysByMonth = [] #holds dictionaries for each month
daysByYear = [] #holds dictionaries for each year

minMaxMonths = []
minMaxYears = []
chartData = []

#colors for the chart
HHHL = "lime" # higher high and higher low
LHLL = "red" # lower high and lower low
HHLL = "sienna" # higher high and lower low
LHHL = "silver" # lower high and higher low

#fill in minMaxMonths
def parseMonths():
    for month in daysByMonth:
        monthMax = max(month.items(), key=operator.itemgetter(1))
        monthMin = min(month.items(), key=operator.itemgetter(1))
        minMaxMonths.append(monthMax)
        minMaxMonths.append(monthMin)

#    for i in minMaxMonths:
#        print(i)
    return

#fill in minMaxYears
def parseYears():
    for year in daysByYear:
        print(year.items())
        yearMax = max(year.items(), key=operator.itemgetter(1))
        yearMin = min(year.items(), key=operator.itemgetter(1))
#        minMaxYears.append(yearMax)
#        minMaxYears.append(yearMin)
        minMaxYears.append([yearMin, yearMax])
    
#    for i in minMaxYears:
#        print(i)

    return

#fill in chartData with the colors (and directions) for the candlesticks
def getColors():
    year = 1950
    for i in range(len(minMaxYears)):
        curLow = (minMaxYears[i][0])[1]
        curHigh = (minMaxYears[i][1])[1]
        chartData.insert(i, [year, curLow, curHigh])
        year += 1
        color = ""
        if i == 0:
            color = HHHL
        else:
            prevLow = (minMaxYears[i-1][0])[1]
            prevHigh = (minMaxYears[i-1][1])[1]
            if curHigh >= prevHigh and curLow >= prevLow:
                color = HHHL
            elif curHigh < prevHigh and curLow < prevLow:
                color = LHLL
            elif curHigh >= prevHigh and curLow < prevLow:
                color = HHLL
            else: # curHigh < prevHigh and curLow >= prevLow
                color = LHHL

        minMaxYears[i].append(color)
        chartData[i].append(color)

        if color == HHLL:
            minDate = (minMaxYears[i][0])[0]
            maxDate = (minMaxYears[i][1])[0]
            if minDate > maxDate:
                direction = "down"
            else:
                direction = "up"
            minMaxYears[i].append(direction)
            chartData[i].append(direction)

#    for i in minMaxYears:
#        print(i)

#    for i in chartData:
#        print(i)

    print("Printing out chart data...")
    with open('toChart.csv', 'w') as outFile:
        wr = csv.writer(outFile)
        wr.writerows(chartData)
    return

#draw the chart using matplotlib
def drawChart():
    print("Drawing the chart...")
    for row in chartData:
        year = [row[0], row[0]]
        values = [row[1], row[2]]
        plt.plot(year, values, color=row[3])
        if row[3] == HHLL:
            if row[4] == "up":
                plt.scatter(row[0], row[2], color=row[3], s=12, marker=6)
            else:
                plt.scatter(row[0], row[1], color=row[3], s=12, marker=7)
    
    plt.yscale('symlog')

    plt.title('SP500')
    plt.xlabel('Year')
    plt.ylabel('(log scale)')
    plt.grid(True)
    plt.show()
    return

def main(argv):
    # parse argument
    if (len(argv) != 2): # incorrect number of arguments
        error('Incorrect usage: chart.py accepts one .csv argument only.\nUSAGE: ./chart.py FILENAME\n')
    else:
        filename = argv[1]
        if (filename.endswith('.csv') == False): # check file type
            error('Incorrect file type: chart.py accepts one .csv argument only.\n')
        else: # open the file
            try:
                file = open(filename, 'r')
                csvFile = csv.reader(file)
            except IOError:
                error('Error: file could not be opened.\n')
            print(f'Parsing the csv {filename}')

    #parse the data in the file
    #and fill in allRows, daysClose, and daysByMonth
    labelRow = 1
    prevMonth = -1
    prevYear = -1
    month = {}
    year = {}
    for row in csvFile:
        if labelRow:
            labelRow = 0
            continue
        for cell in row:
            cellList = cell.split("/")
            if int(cellList[2]) >= 50:
                date = datetime.date(int(cellList[2])+1900, int(cellList[0]), int(cellList[1]))
            else:
                date = datetime.date(int(cellList[2])+2000, int(cellList[0]), int(cellList[1]))
            break
        row[0] = date
        allRows.append(row)
        daysClose[date] = float(row[4])
        
        if date.month == prevMonth or prevMonth == -1:
            month[date] = float(row[4])
        else:
            daysByMonth.append(month)
            if date.month == 1:
                temp = {max(month): month[max(month)]}
                month = temp
            else:
                month = {}
            month[date] = float(row[4])
        prevMonth = date.month

        if date.year == prevYear or prevYear == -1:
            year[date] = float(row[4])
        else:
            daysByYear.append(year)
            if date.month == 1:
                temp = {max(year): year[max(year)]}
                year = temp
            else:
                year = {}
            year[date] = float(row[4])
        prevYear = date.year
            
    daysByMonth.append(month)

#    for i in daysByYear:
#        print(i)

    parseMonths()
    parseYears()
    getColors()
    drawChart()

if __name__ == "__main__":
    main(sys.argv)
