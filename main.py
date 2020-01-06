import csv
from random import shuffle

print("Programmes zur Erstellung des Planes für den Technik^3 Tag\nV.0.1\n")

plans = [[[], float("inf")]]  # plan| cost of plan
length = int(input("Wieviele Berechnungen sollen vorgenommen werden?"))
slots = {"number of slots": int(input("Wie viele Slots werden benötigt?"))}

for run in range(0, length):
    groups = []  # one dictionary per group
    stations = []  # one dictionary per station

    plan = []
    cost = 0

    # copying groups in RAM
    with open("groups.csv", newline="") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=";", quotechar='"')
        for line in csvreader:
            groups.append({"name": line[0],
                           "used slots": [],
                           "visited stations": []})

    # copying stations in RAM
    with open("stations.csv", newline="") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=";", quotechar='"')
        for line in csvreader:
            stations.append({"name": line[0],
                             "slots per group": int(line[1]),
                             "groups per slot": int(line[2]),
                             "used slots": [],
                             "educated groups": [],
                             "running": 0})

    # slot by slot
    for current_slot in range(0, slots["number of slots"]):
        shuffle(stations)
        # one station at a time
        for station in stations:

            # if a station would be longer than allowed educating a single group of groups,
            if station["running"] >= station["slots per group"]:
                # it will get another group
                station["running"] = 0
            # if a group is already at this station the station doesn't get another group
            if station["running"] > 0:
                station["educated groups"].append("Running")
                station["running"] = station["running"] + 1
                continue

            # when station doesn't finnish educating a group, it won't even start
            if current_slot + station["slots per group"] > slots["number of slots"]:
                # to prevent this problem this station doesn't educate anyone
                continue

            # the station gets as many groups as it can educate at a point in time
            for x in range(0, station["groups per slot"]):
                shuffle(groups)
                hit = False
                # seeking a group
                for group in groups:

                    # which has free time and was not at this station before
                    if current_slot + 1 not in group["used slots"] and station["name"] not in group["visited stations"]:
                        hit = True
                        group["visited stations"].append(station["name"])
                        station["educated groups"].append(group["name"])

                        # making the station and group/s stay together as long as needed
                        for n in range(0, station["slots per group"]):
                            station["used slots"].append(current_slot + 1 + n)
                            group["used slots"].append(current_slot + 1 + n)
                            if station["slots per group"] > 1 and n >= 1:
                                group["visited stations"].append("Running")

                        # if the station needs more than one slot per group it'll be skipped next time
                        if station["slots per group"] > 1:
                            station["running"] = 1
                        break
                # if the station doesn't get a group
                if not hit:
                    station["educated groups"].append("None")

        # if group isn't visiting a station this time
        for group in groups:
            if current_slot + 1 not in group["used slots"]:
                group["visited stations"].append("None")

    # creating plan to print into csv
    plan.append(["slot"])
    for slot in range(0, slots["number of slots"]):
        plan[len(plan) - 1].append(str(slot + 1))
    # sorting stations
    stations.sort(key=lambda sort_station: sort_station["name"])
    # going threw every station
    for idx, station in enumerate(stations):
        # creating list with name as first item as new item in plan
        plan.append([station["name"]])
        # current index in raw station
        n = 0
        # current index in station in plan
        x = 1
        # adding groups in slots to station in plan
        while n < len(station["educated groups"]):
            plan[idx + 1].append([])
            # adding as many items into one as groups per slot
            problem = True
            for i in range(0, station["groups per slot"]):
                if n >= len(station["educated groups"]):
                    problem = False
                    break

                # if the station is still educating a group/s there will only be one "Running"
                if station["educated groups"][n] == "Running":
                    plan[idx + 1][x] = ["Running"]
                    n = n + 1
                    problem = False
                    break

                if station["educated groups"][n] == "None":
                    cost = cost + 1
                else:
                    problem = False
                plan[idx + 1][x].append(station["educated groups"][n])
                # elevating index
                n = n + 1
            # if a station doesn't get a single group this time the cost will be elevated
            if problem:
                cost = cost + 2
            x = x + 1

    # adding pauses
    plan_pause_idx = len(plan)
    plan.append(["pause"])
    for slot in range(0, slots["number of slots"]):
        plan[plan_pause_idx].append([])
        for group in groups:
            if slot + 1 not in group["used slots"]:
                plan[plan_pause_idx][slot + 1].append(group["name"])

    # adding plan for groups
    groups.sort(key=lambda sort_group: sort_group["name"])
    plan.append([])
    plan.append(["slot"])
    for slot in range(0, slots["number of slots"]):
        plan[len(plan) - 1].append(str(slot + 1))

    for group in groups:
        plan.append([group["name"]])
        for station in group["visited stations"]:
            plan[len(plan) - 1].append(station)
    for group in groups:
        count = 0
        for station in group["visited stations"]:
            if station == "None":
                count = 2 * count + 0.5
                cost = cost + count
    plans.append([plan, cost])

    # sorting plans and deleting everyone except best
    plans.sort(key=lambda sort_plan: sort_plan[1])
    plans = [plans[0]]
    # printing current status
    if run % int(round(length / 100 + 0.5)) == 0 and run != 0:
        # print(str(int(run / length * 100)) + "%  cost = " + str(plans[0][1]))
        print(str(int(run / length * 100)) + "%")

# selecting best plan and extracting plan and cost
plans.sort(key=lambda sort_plan: sort_plan[1])
plan = plans[0][0]
cost = plans[0][1]

# writing plan into csv
with open("plan.csv", "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # turning list of groups in one slot into one list
    for station in plan:
        station_ready = []
        for slot in station:
            if type(slot) == list:
                station_ready.append(", ".join(slot))
            else:
                station_ready.append(slot)

        csv_writer.writerow(station_ready)

# print("100%  cost = " + str(cost))
input("100%\nProzess beendet, die Tabelle ist in plan.csv vorzufinden.\n(Das Fenster kann nun geschlossen werden.)")
