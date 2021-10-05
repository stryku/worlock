from datetime import datetime
import json
import collections


current_day = ''
current_in = ''
current_in_line_i = 0
days = {}


def access_day(day):
    global days

    if day not in days:
        days[day] = {
            'ranges': [],
            'deltas': []
        }

    return days[day]


def delta_to_seconds(delta: str) -> int:
    result = 1
    if delta[0] == '-':
        result = -1

    delta = delta[1:]
    amount, unit = delta.split()

    mul = 1
    if unit == 'min':
        mul = 60
    elif unit == 'h':
        mul = 60*60

    return result * int(amount) * mul


def range_to_seconds(r) -> int:
    begin, end = r

    begin = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')

    return (end - begin).seconds


line_i = 0

for line in open('worlock.md', 'r').readlines():
    line_i += 1

    # remove \n
    line = line.strip()

    if not line:
        continue

    if line.startswith('#'):
        continue

    print(f'Processing line[{line_i}]: {line}')

    if line.startswith('+') or line.startswith('-'):
        # Got +30 min or -1 h

        if not current_day:
            print(f'Found delta not within range. Line [{line_i}]: {line}')
            exit(1)

        split = line.split()
        if not split[0][1:].isnumeric() or split[1] not in ['min', 'h']:
            print(f'Found malformed delta. Line [{line_i}]: {line}')
            exit(1)

        day = access_day(current_day)
        day['deltas'].append(line)
    else:
        split = line.split()
        if split[0] == 'in':
            if current_in:
                print(
                    f'Found not closed in. Line [{current_in_line_i}]: {current_in}')
                exit(1)

            current_in = line
            current_in_line_i = line_i
            current_day = split[1]
        elif split[0] == 'out':
            if not current_in:
                print(f'Found not matched out. Line [{line_i}]: {line}')
                exit(1)

            if line.split()[1] != current_day:
                print(
                    f'Found not closed in. Line [{current_in_line_i}]: {current_in}')
                exit(1)

            day = access_day(current_day)
            in_begin = current_in.split(maxsplit=1)[1]
            out_end = line.split(maxsplit=1)[1]
            day['ranges'].append((in_begin, out_end))

            current_in = ''
            current_day = ''

        else:
            print(f'Found not known option. Line [{line_i}]: {line}')

if current_in:
    print(f'Found not closed in. Line [{current_in_line_i}]: {current_in}')
    exit(1)

days = collections.OrderedDict(days.items())

print(json.dumps(days, indent=1))


months = collections.OrderedDict()

for day, entry in days.items():
    result_s = 0

    for r in entry['ranges']:
        result_s += range_to_seconds(r)

    for delta in entry['deltas']:
        result_s += delta_to_seconds(delta)

    month = day[:7]

    if month not in months:
        months[month] = 0

    months[month] += result_s

for month, seconds in months.items():
    print(f'{month} = {seconds / 3600:.2f}')
