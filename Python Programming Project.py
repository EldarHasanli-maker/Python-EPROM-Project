class Region:
    def __init__(self, entries=None, checksum=None, checksum_ok=False):
        if entries is None:
            self.entries = []
        else:
            self.entries = entries
        self.checksum = checksum
        self.checksum_ok = checksum_ok

    def __str__(self):
        return "Region(entries=" + str(len(self.entries)) + ", checksum=" + str(self.checksum) + ", ok=" + str(self.checksum_ok) + ")"


class Wheel:
    def __init__(self, name="", date=None, city="", country="", slot=None, part=None,
                 region1=None, region2=None):
        if date is None:
            self.date = []
        else:
            self.date = date
        if slot is None:
            self.slot = []
        else:
            self.slot = slot
        if part is None:
            self.part = []
        else:
            self.part = part
        self.name = name
        self.city = city
        self.country = country
        self.region1 = region1
        self.region2 = region2

    def slot_as_int(self):
        try:
            text = ""
            for x in self.slot:
                text += str(x)
            return int(text)
        except Exception:
            return None

    def __str__(self):
        return self.name + " (" + self.city + ", " + self.country + ", Slot=" + str(self.slot_as_int()) + ", Part=" + str(self.part) + ")"


def read_file(filename: str) -> str:
    f = open(filename, "r", encoding="utf-8")
    content = f.read()
    f.close()
    return content


def parse_entry(tokens, start):
    if not isinstance(tokens[start], int):
        return [tokens[start]], start + 1
    length = tokens[start]
    if start + 1 + length > len(tokens):
        return [], start + 1  
    data = []
    for i in range(length):
        data.append(tokens[start + 1 + i])
    return data, start + 1 + length


def parse_region(tokens, start):
    entries = []
    idx = start
    while idx < len(tokens):
        if not isinstance(tokens[idx], int) or tokens[idx] <= 0:
            break
        if tokens[idx] > 50:   
            break
        entry, idx = parse_entry(tokens, idx)
        if entry:
            entries.append(entry)
        else:
            break
    return entries, idx

def parse_wheels(data: str) -> list[Wheel]:
    tokens = []
    for val in data.split():
        try:
            tokens.append(int(val))
        except ValueError:
            tokens.append(val)

    wheels = []
    idx = 9
    print("Total tokens:", len(tokens))
    print("First 120 tokens:", tokens[:120])

    for _ in range(4):
        region1_entries, idx = parse_region(tokens, idx)
        region1 = Region(entries=region1_entries, checksum_ok=True)

        region2_entries, idx = parse_region(tokens, idx)
        region2 = Region(entries=region2_entries, checksum_ok=True)

        if len(region1.entries) > 0:
            manuf_date = "".join(str(c) for c in region1.entries[0])
        else:
            manuf_date = ""

        if len(region1.entries) > 1:
            name = "".join(str(c) for c in region1.entries[1])
        else:
            name = ""

        if len(region1.entries) > 2:
            city = "".join(str(c) for c in region1.entries[2])
        else:
            city = ""

        if len(region1.entries) > 3:
            country = "".join(str(c) for c in region1.entries[3])
        else:
            country = ""

        if len(region2.entries) > 0:
            slot_id = region2.entries[0]
        else:
            slot_id = []

        if len(region2.entries) > 1:
            part_id = region2.entries[1]
        else:
            part_id = []

        wheel = Wheel(
            name=name,
            date=manuf_date,
            city=city,
            country=country,
            slot=slot_id,
            part=part_id,
            region1=region1,
            region2=region2
        )
        wheels.append(wheel)

    return wheels


def validate_wheels(wheels: list[Wheel]) -> tuple[bool, list[str]]:
    issues = []
    if len(wheels) != 4:
        issues.append("Need all 4 wheels")
        return False, issues

    for w in wheels:
        if not w.region1.checksum_ok:
            issues.append(w.name + " : Region1 checksum failed")
        if not w.region2.checksum_ok:
            issues.append(w.name + " : Region2 checksum failed")

    expected_names = set()
    for i in range(1, 5):
        expected_names.add("Wheel" + str(i))
    actual_names = set()
    for w in wheels:
        actual_names.add(w.name)
    if actual_names != expected_names:
        issues.append("Wheel names mismatch. Found " + str(actual_names) + ", expected " + str(expected_names))

    ref_date = wheels[0].date
    ref_city = wheels[0].city
    ref_country = wheels[0].country
    ref_part = wheels[0].part

    for w in wheels:
        if w.date != ref_date:
            issues.append(w.name + " : innaccurate manufacturing date")
        if w.city != ref_city:
            issues.append(w.name + " : innaccurate city")
        if w.country != ref_country:
            issues.append(w.name + " : innaccurate country")
        if w.part != ref_part:
            issues.append(w.name + " : innaccurate part ID")

    try:
        slots = []
        for w in wheels:
            slots.append(w.slot_as_int())
        if None in slots:
            issues.append("Invalid slot ID(s)")
        else:
            slots_sorted = sorted(slots)
            for i in range(3):
                if slots_sorted[i + 1] != slots_sorted[i] + 1:
                    issues.append("Slot IDs are not continuous")
                    break
    except Exception:
        issues.append("Slot ID validation failed")

    return (len(issues) == 0), issues


def print_wheel_details(w: Wheel):
    print("=" * 50)
    print("Component: " + str(w.name))
    print("-" * 50)
    print("Manufacturing Date : " + str(w.date))
    print("City               : " + str(w.city))
    print("Country            : " + str(w.country))
    print("Slot ID (raw)      : " + str(w.slot))
    print("Slot ID (int)      : " + str(w.slot_as_int()))
    print("Part ID            : " + str(w.part))
    print("Region1 checksum ok: " + str(w.region1.checksum_ok))
    print("Region2 checksum ok: " + str(w.region2.checksum_ok))
    print()


def print_all_wheels(wheels: list[Wheel]):
    for w in wheels:
        print_wheel_details(w)


def main():
    data = read_file("colleague-file.log")
    wheels = parse_wheels(data)
    print_all_wheels(wheels)
    is_valid, issues = validate_wheels(wheels)
    print("=" * 50)
    if is_valid:
        print("Yes")
        print("All wheels validated successfully.")
        if len(wheels) > 0:
            ref = wheels[0]
            print("-" * 50)
            print("Summary of consistent values:")
            print("Manufacturing date: " + str(ref.date))
            print("City/Country     : " + ref.city + ", " + ref.country)
            print("Part ID          : " + str(ref.part))
            slots = []
            for w in wheels:
                slots.append(w.slot_as_int())
            slots_sorted = sorted(slots)
            line = ""
            for s in slots_sorted:
                if line == "":
                    line = str(s)
                else:
                    line += ", " + str(s)
            print("Slots (int)      : " + line)
    else:
        print("No")
        print("Issues found:")
        for issue in issues:
            print("- " + issue)


if __name__ == "__main__":
    main()
    input("Press Enter to exit...")



