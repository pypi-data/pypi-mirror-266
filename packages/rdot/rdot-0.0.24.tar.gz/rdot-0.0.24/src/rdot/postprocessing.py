"""Tools for ensuring monotonicity, smoothness of rate-distortion bounds."""

import numpy as np

def compute_lower_bound(rd_points: list[tuple[float]]) -> np.ndarray:
    """Remove all points in a rate-distortion curve that would make it nonmonotonic and return only the resulting monotonic indices.

    This is required to remove the random fluctuations in the result induced by the BA algorithm getting stuck in local minima.
    
    Acknowledgement: https://github.com/epiasini/embo-github-mirror/blob/master/embo/utils.py#L77.
    
    Args:
        rd_points: list of pairs of floats, where each pair represents an estimated (rate, distortion) pair, and *ordered by increasing rate*.

    Returns:
        selected_indices: 1D array of shape  `(num_selected, )` containing the indices of the points selected to ensure monotonically decreasing values
    """
    pts = np.array(rd_points)
    selected_indices = [0]

    for idx in range(1,pts.shape[0]):
        # Check that each point increases in rate and does not increase in distortion.
        if (
            # TODO: analysis has revealed that this condition might be too strong for numerical precision. Consider using an atol of 1e-10 when computing these inequalities
            pts[idx,0] >= pts[selected_indices[-1],0] 
            and pts[idx,1] <= pts[selected_indices[-1],1]
        ):
            selected_indices.append(idx)
            
    return selected_indices