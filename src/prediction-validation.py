import sys

def round_to(n, number):
  spec = "{:." + str(n) + "f}"
  return spec.format(float(number))

def abs_diff(lhs, rhs):
  return round_to(2, abs(float(lhs) - float(rhs)))

def average(lhs, rhs):
  return round_to(2, float(lhs) / float(rhs))

# =========================================================
# Remove new line from a given string
# =========================================================
# Example:
#
# input: "hello world\n"
#
# outout: "hello world"
# =========================================================
def remove_new_line(line):
  return line.replace("\n", "")


def empty_line(line):
  return line != ""


def parse_window(lines):
  return int(lines[0])

def get_at(list, index, default=None):
  return (list[index] if list[index:index+1] else default)

def parse_record_to_line(record):
  return "|".join([
    str(record["start_time"]),
    str(record["end_time"]),
    round_to(2, record["average_error"]),
  ])

def parse_records_to_lines(records):
  return [parse_record_to_line(record) for record in records]

# =========================================================
# Parse given string and map it to RECORD
# - RECORD is a dictionary contains "time", "stock", "price"
# =========================================================
# Example:
#
# input: "1|EDMMCA|25.80"
#
# outout: {time: 1, "stock": "EDMMCA", "price": 25.80}
# =========================================================
def parse_record(line):
  columns = line.split("|")

  return {
    "time": int(columns[0]),
    "stock": columns[1],
    "price": columns[2]
  }

# =========================================================
# Parse a list of strings and map them to RECORDS
# =========================================================
# Example:
#
# input: ["1|EDMMCA|25.80\n", "1|AMDDPW|23.46\n", ...]
#
# outout: [
#   {time: 1, "stock": "EDMMCA", 25.80},
#   {time: 1, "stock": "AMDDPW", 23.46}
# ]
# =========================================================
def parse_lines_to_records(lines):
  return [parse_record(remove_new_line(line)) for line in lines]

# =========================================================
# Take a list of records and group predicted prices by
# time and stock (in that order)
# =========================================================
# Example:
#
# input: [
#   {"time": 1, "stock": "AMDDPW", "price": 23.46,
#   {"time": 1, "stock": "CCKENL", "price": 25.27,
#   {"time": 1, "stock": "NELVVI", "price": 22.41,
#   {"time": 1, "stock": "LWZQMJ", "price": 19.14,
#   {"time": 2, "stock": "AMDDPW", "price": 22.48,
#   {"time": 2, "stock": "CCKENL", "price": 24.75,
#   {"time": 2, "stock": "LWZQMJ", "price": 17.26,
#   {"time": 2, "stock": "QMQNMQ", "price": 26.22,
#   {"time": 3, "stock": "AMDDPW", "price": 26.39,
#   {"time": 3, "stock": "YZSGPL", "price": 21.29,
#   {"time": 3, "stock": "CCKENL", "price": 21.73,
#   {"time": 3, "stock": "NELVVI", "price": 26.42
# ]
#
# output: {
#   1: {
#     "AMDDPW": 23.46,
#     "CCKENL": 25.27,
#     "NELVVI": 22.41,
#     "LWZQMJ": 19.14
#   },
#   2: {
#     "AMDDPW": 22.48,
#     "CCKENL": 24.75,
#     "LWZQMJ": 17.26,
#     "QMQNMQ": 26.22
#   },
#   3: {
#     "AMDDPW": 26.39,
#     "YZSGPL": 21.29,
#     "CCKENL": 21.73,
#     "NELVVI": 26.42
#   }
# }
# =========================================================
def build_predicted_tree(records):
  tree = {}

  # traverse through all given records
  for record in records:
    # double check if given time exists or not
    # set it to a new dictionary if it does not exist
    tree[record["time"]] = tree.get(record["time"], {})

    # set the price to by time and stock
    tree[record["time"]][record["stock"]] = record["price"]

  return tree

def merge_predicted(records, predicted_tree):
  for record in records:
    time = record["time"]
    stock = record["stock"]
    price = record["price"]

    predicted_price = predicted_tree.get(time, {}).get(stock, None)
    error = abs_diff(price, predicted_price) if predicted_price else None

    record["predicted_price"] = predicted_price
    record["error"] = error

  return records

def group_by_time(records):
  grouped_records = {}

  for record in records:
    time = record["time"]
    grouped_records[time] = grouped_records.get(time, [])
    grouped_records[time].append(record)

  return grouped_records

def build_time_window_group(start_time, window):
  return {
    "start_time": start_time,
    "end_time": start_time + window - 1,
    "records": []
  }

def group_by_window(time_grouped_records, window):
  grouped_records = []
  number_of_window = len(time_grouped_records) - window + 1

  begin = [i for i in time_grouped_records.keys()][0]

  for start_time in range(begin, begin + number_of_window):
    group = build_time_window_group(start_time, window)

    for index in range(0, window):
      time = start_time + index
      records_at_time = time_grouped_records.get(time, [])
      group["records"].extend(records_at_time)

    grouped_records.append(group)

  return grouped_records

def calculate_average(records):
  errors = [float(record["error"]) for record in records if record["error"] != None]

  size = len(errors)

  error_sum = sum(errors)

  return average(error_sum, size)

def summarize(window_grouped_records):
  for group in window_grouped_records:

    records = group["records"]

    average = calculate_average(records)

    group["average_error"] = average

  return window_grouped_records


# =========================================================
# Load a file from given path and read all the lines
# =========================================================
# Example:
#
# input: "./input/actual.txt"
#
# output: ["1|EDMMCA|25.80\n", "1|AMDDPW|23.46\n", ...]
# =========================================================
def load(path):
  with open(path, "r") as file:
    lines = file.readlines()
  return lines


def save(path, lines):
  with open(path, "w") as file:
    content = "\n".join(lines) + "\n"
    file.write(content)

# =========================================================
# Parse system arguments from list to dictionary
# =========================================================
# Example:
#
# input: [
#   "./input/actual.txt",
#   "./input/predicted.txt",
#   "./output/comparison.txt"
#  ]
#
# output: {
#   "actual": "./input/actual.txt",
#   "predicted": "./input/predicted.txt",
#   "output": "./output/comparison.txt"
# }
# =========================================================
def parse_arguments(args):
  return {
    "window": args[1],
    "actual": args[2],
    "predicted": args[3],
    "output": args[4]
  }

# =========================================================
# main function
# =========================================================
def run():
  # convert system arguments to options
  opts = parse_arguments(sys.argv)

  lines = load(opts["window"])
  window = parse_window(lines)

  # load actual file from given path
  lines = load(opts["actual"])

  # convert each line from a string to a record
  actual_records = parse_lines_to_records(lines)

  # load predicted file from given path
  lines = load(opts["predicted"])

  # convert each line from a string to a record
  predicted_records = parse_lines_to_records(lines)

  # convert predicted records into predicted tree for better search
  predicted_tree = build_predicted_tree(predicted_records)

  # generate comparison data
  records = merge_predicted(actual_records, predicted_tree)

  time_grouped_records = group_by_time(records)

  window_grouped_records = group_by_window(time_grouped_records, window)

  summarize_records = summarize(window_grouped_records)

  lines = parse_records_to_lines(summarize_records)

  save(opts["output"], lines)

run()

