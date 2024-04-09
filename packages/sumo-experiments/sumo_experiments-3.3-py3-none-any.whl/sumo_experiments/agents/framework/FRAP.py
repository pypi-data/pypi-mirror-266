import matplotlib.pyplot as plt

from sumo_experiments.agents import Agent
import traci
import numpy as np


class FRAP(Agent):
    """
    Implements the framework FRAP basemodel for an agent, described by Zheng et al in [1].

    [1] Zheng, G., Xiong, Y., Zang, X., Feng, J., Wei, H., Zhang, H., ... & Li, Z. (2019, November). Learning phase competition for traffic signal control. In Proceedings of the 28th ACM international conference on information and knowledge management (pp. 1963-1972).
    """

    def __init__(self,
                 id_intersection,
                 id_tls_program,
                 intersection_relations,
                 length_detector):
        """
        Init of class.
        :param id_intersection: The id of the intersection the agent will control
        :type id_intersection: str
        :param id_tls_program: The id of the traffic light program related to the intersection
        :type id_tls_program: str
        :param intersection_relations: The relations for this intersection.
        :type intersection_relations: dict
        """
        super().__init__()
        self.started = False
        self.id_intersection = id_intersection
        self.id_tls_program = id_tls_program
        self.current_phase = 0
        self.countdown = 0
        self.time_countdown = 0
        self.relations = intersection_relations
        self.current_max_time_index = 0
        self.count_function = traci.lanearea.getLastStepVehicleNumber
        self.length_detector = length_detector

    def get_state_values(self):
        """
        Get the values required to compute the current state of the agent, i.e. the demand for each phase and the current phase.
        :return: The values of each 
        """

    def numerical_detectors_red_lanes(self):
        """
        Return the numerical detectors related to red lanes for a phase.
        :return: The list of all concerned detectors
        :rtype: list
        """
        detectors = []
        current_phase = traci.trafficlight.getRedYellowGreenState(self.id_tls_program)
        phases = traci.trafficlight.getControlledLinks(self.id_tls_program)
        for i in range(len(current_phase)):
            link = current_phase[i]
            if link == 'r':
                link_infos = phases[i]
                for info in link_infos:
                    lane = info[0]
                    lane_number = int(lane.split('_')[-1])
                    edge = lane[:-2]
                    edge_index = self.relations['related_edges'].index(edge)
                    detector = self.relations['related_numerical_detectors'][edge_index][lane_number]
                    if detector not in detectors:
                        detectors.append(detector)
        return detectors

    def numerical_detectors_green_lanes(self):
        """
        Return the detectors related to green lanes entry for a phase.
        :return: The list of all concerned detectors
        :rtype: list
        """
        detectors = []
        current_phase = traci.trafficlight.getRedYellowGreenState(self.id_tls_program)
        phases = traci.trafficlight.getControlledLinks(self.id_tls_program)
        for i in range(len(current_phase)):
            link = current_phase[i]
            if link == 'g' or link == 'G':
                link_infos = phases[i]
                for info in link_infos:
                    lane = info[0]
                    lane_number = int(lane.split('_')[-1])
                    edge = lane[:-2]
                    edge_index = self.relations['related_edges'].index(edge)
                    detector = self.relations['related_numerical_detectors'][edge_index][lane_number]
                    if detector not in detectors:
                        detectors.append(detector)
        return detectors


if __name__ == "__main__":
    pass