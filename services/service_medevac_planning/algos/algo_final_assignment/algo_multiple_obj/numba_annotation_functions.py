import numba
from numba.typed import List
@numba.njit(cache=True)
def rts_ann_fn(annotations, weights):
    """
        Calculate the Revised Trauma Score (RTS) based on PyReason rule annotations.

        This function computes the normalized RTS using Glasgow Coma Scale (GCS), Systolic Blood Pressure (SBP),
        and Respiratory Rate (RR) from the rule annotations.

        Args:
            annotations (list): List of PyReason rule body annotations for RTS calculation.
            weights (list): List of weights (not used in this function).

        Returns:
            tuple: A tuple containing:
                - final_score (float): The calculated RTS score, rounded to 2 decimal places. (0: low severity, 1: highest severity)
                - 1 (int): A constant value of 1.
        """
    def get_normalized_gcs(gcs):
        if gcs == 3:
            return 0
        if gcs in [4, 5]:
            return 1
        if gcs in [6, 7, 8]:
            return 2
        if gcs in [9, 10, 11, 12]:
            return 3
        if gcs in [13, 14, 15]:
            return 4

    def get_normalized_sbp(sbp):
        if sbp == 0:
            return 0
        if sbp > 0 and sbp < 49:
            return 1
        if sbp >= 49 and sbp < 75:
            return 2
        if sbp >= 75 and sbp < 89:
            return 3
        if sbp >= 89:
            return 4

    def get_normalized_rr(rr):
        if rr == 0:
            return 0
        if rr > 0 and rr < 5:
            return 1
        if rr >= 5 and rr < 9:
            return 2
        if rr >= 9 and rr < 29:
            return 4
        if rr >= 29:
            return 3

    # print(annotations)
    gcs = annotations[4][0].lower * 1000
    sbp = annotations[5][0].lower * 1000
    rr = annotations[6][0].lower * 1000

    normalized_gcs = get_normalized_gcs(gcs)
    normalized_sbp = get_normalized_sbp(sbp)
    normalized_rr = get_normalized_rr(rr)
    rts_score = normalized_gcs + normalized_sbp + normalized_rr
    final_score = round((12 - rts_score) / 12, 2)

    return final_score, 1
@numba.njit(cache=True)
def niss_ann_fn(annotations, weights):
    """
        Calculate the New Injury Severity Score (NISS) based on PyReason rule annotations.

        This function computes the normalized NISS using normalized Abbreviated Injury Scale (AIS) scores
        for different body regions from the rule annotations.

        Args:
            annotations (list): List of PyReason rule body annotations for NISS calculation.
            weights (list): List of weights (not used in this function).

        Returns:
            tuple: A tuple containing:
                - final_score (float): The calculated NISS score, rounded to 2 decimal places.(0: low severity, 1: highest severity)
                - 1 (int): A constant value of 1.
        """
    def find_three_max(numba_list):
        # Initialize three variables to store the maximum values
        max1, max2, max3 = -1,-1,-1

        for num in numba_list:
            if num > max1:
                max3 = max2
                max2 = max1
                max1 = num
            elif num > max2:
                max3 = max2
                max2 = num
            elif num > max3:
                max3 = num

        return max1, max2, max3
    ais_list = List()  # Create an empty typed list

    ais_list.append(float(annotations[9][0].lower*10))
    ais_list.append(float(annotations[10][0].lower*10))
    ais_list.append(float(annotations[11][0].lower*10))
    ais_list.append(float(annotations[12][0].lower*10))
    ais_list.append(float(annotations[13][0].lower*10))
    ais_list.append(float(annotations[14][0].lower*10))
    ais_list.append(float(annotations[15][0].lower*10))
    ais_list.append(float(annotations[16][0].lower*10))

    max1, max2, max3 = find_three_max(ais_list)
    niss_score = max1*max1 + max2*max2 + max3*max3
    if niss_score > 75:
        niss_score = 75
    if niss_score == 0:
        final_score = 0.00001
    else:
        final_score = round(1-((75-niss_score) / 75), 2)
    return final_score, 1

@numba.njit(cache=True)
def life_ann_fn(annotations, weights):
    """
        Calculate a normalized life score based on NISS and RTS scores from PyReason rule annotations.

        This function computes a normalized life score by averaging the NISS and RTS scores
        obtained from the rule annotations.

        Args:
            annotations (list): List of PyReason rule body annotations containing NISS and RTS scores.
            weights (list): List of weights (not used in this function).

        Returns:
            tuple: A tuple containing:
                - final_score (float): The calculated normalized life score, rounded to 2 decimal places.(0: low severity, 1: highest severity)
                - 1 (int): A constant value of 1.
        """
    niss_score = annotations[1][0].lower
    rts_score = annotations[2][0].lower

    life_score = (niss_score+rts_score)/2
    final_score = round(life_score,2)
    return final_score,1

@numba.njit(cache=True)
def final_niss_ann_fn(annotations, weights):
    """
        Extract the final NISS score from PyReason rule annotations.

        This function returns the NISS score from the rule annotations.

        Args:
            annotations (list): List of PyReason rule body annotations containing the NISS score.
            weights (list): List of weights (not used in this function).

        Returns:
            tuple: A tuple containing:
                - final_score (float): The normlaized NISS score.
                - 1 (int): A constant value of 1.
        """
    niss_score = annotations[1][0].lower
    final_score = niss_score
    return final_score, 1

@numba.njit(cache=True)
def final_rts_ann_fn(annotations, weights):
    """
        Extract the final RTS score from PyReason rule annotations.

        This function returns the RTS score from the rule annotations.

        Args:
            annotations (list): List of PyReason rule body annotations containing the RTS score.
            weights (list): List of weights (not used in this function).

        Returns:
            tuple: A tuple containing:
                - final_score (float): The normalized RTS score.
                - 1 (int): A constant value of 1.
        """
    rts_score = annotations[1][0].lower
    final_score = rts_score
    return final_score, 1