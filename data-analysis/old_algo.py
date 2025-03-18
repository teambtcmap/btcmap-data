 # Calculate area score based on the current set of areas
 max_total_merchants = max((other_area.total_merchants or 0)
                           for other_area in areas)
  max_weighted_average_verification_age = max(
       (other_area.weighted_average_verification_age or 0) for other_area in areas)

   if max_total_merchants == 0:
        normalized_total_merchants = 0
    else:
        normalized_total_merchants = area.total_merchants / max_total_merchants

    if max_weighted_average_verification_age == 0 or area.weighted_average_verification_age is None:
        normalized_weighted_average_verification_age = 0
    else:
        normalized_weighted_average_verification_age = area.weighted_average_verification_age / \
            max_weighted_average_verification_age

    # Sum of the weights should be 1
    weight_total_merchants = 0.2
    weight_weighted_average_verification_age = 0.8

    if area.weighted_average_verification_age is not None:
        area.score = (weight_total_merchants * normalized_total_merchants) + (
            weight_weighted_average_verification_age * (1 - normalized_weighted_average_verification_age))
    else:
        # Assign a low score when the weighted_average_verification_age is None
        area.score = 0.1  # You can adjust the low score value as needed
