            c = 0.5  # You can adjust this value

            max_population = max(area.population for area in areas if area.population)
            max_total_merchants = max(area.total_merchants for area in areas if area.total_merchants)
            max_up_to_date_merchants = max(
                latest_report.up_to_date_elements
                for area in areas
                for latest_report in area.reports
            )

            if (
                area.total_merchants is not None
                and max_total_merchants != 0
                and area.population is not None
                and max_population != 0
                and latest_report.up_to_date_elements is not None
                and max_up_to_date_merchants != 0
            ):
                score = (
                    (c + (math.log(area.total_merchants) / math.log(max_total_merchants))) /
                    (c + 1)
                ) * (
                    (math.log(area.population) / math.log(max_population)) *
                    ((latest_report.up_to_date_elements / max_up_to_date_merchants) ** 2)
                )
            else:
                score = 0  # Handle the division by zero or None case

            area.score = score