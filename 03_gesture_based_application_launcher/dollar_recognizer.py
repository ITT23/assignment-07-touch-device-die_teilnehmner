import os
import xml.etree.ElementTree as ET
from typing import List

from dollarpy import Point, Recognizer, Template


class Dollar_Recognizer:
    def __init__(self, gestures) -> None:
        self.templates = self.get_templates(gestures)
        self.recognizer = Recognizer(self.templates)

    def get_templates(self, gestures) -> List[Template]:
        templates = []
        for root, _, files in os.walk('03_gesture_based_application_launcher/gesture_templates'):
            for file in files:
                fname = file.split('.')[0]
                label = fname[:-2]
                if label not in gestures:
                    continue

                xml_root = ET.parse(f'{root}/{file}').getroot()

                points = []
                for element in xml_root.findall('Point'):
                    x = element.get('X')
                    y = element.get('Y')
                    points.append([int(x), int(y)])

                transformed = self.transform(points=points)

                templates.append(Template(label, transformed))
        return templates

    def recognize(self, points: List[List[int]]):
        transformed_points = self.transform(points=points)
        result = self.recognizer.recognize(points=transformed_points)

        return result

    def transform(self, points: List[List[int]]) -> List[Point]:
        transformed = []
        for point in points:
            transformed_point = Point(point[0], point[1])
            transformed.append(transformed_point)

        return transformed
