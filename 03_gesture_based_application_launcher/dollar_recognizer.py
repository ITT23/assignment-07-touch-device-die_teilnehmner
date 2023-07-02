'''
Implementation of Wobbock et al's One Dollar Recognizer.
'''
import os
import xml.etree.ElementTree as ET
from typing import List

from dollarpy import Point, Recognizer, Template


class Dollar_Recognizer:
    def __init__(self, gestures: List[str]) -> None:
        '''
        Sets up recognizer and list of known gestures

        Args:
            List[str]: List of gestures the recognizer should be able to distinguish
        '''
        self.templates = self.get_templates(gestures)
        self.recognizer = Recognizer(self.templates)

    def get_templates(self, gestures: List[str]) -> List[Template]:
        '''
        Transforms gestures labels to dollarpy Templates.
        Templates are created from xml files in './gesture_templates'

        Args:
            List[str]:  List of gesture labels

        Returns:
            List[Template]: List of dollarpy Templates
        '''
        templates: List[Template] = []
        for root, _, files in os.walk('03_gesture_based_application_launcher/gesture_templates'):
            for file in files:
                fname = file.split('.')[0]
                label = fname[:-2]
                if label not in gestures:
                    continue

                xml_root = ET.parse(f'{root}/{file}').getroot()

                points: List[List[int]] = []
                for element in xml_root.findall('Point'):
                    x = element.get('X')
                    y = element.get('Y')
                    points.append([int(x), int(y)])

                transformed = self.transform(points=points)

                templates.append(Template(label, transformed))
        return templates

    def recognize(self, points: List[List[int]]) -> tuple[str | None, float]:
        '''
        Maps list of coordinates to a gesture

        Args:
            List[List[int]]: List of coordinates

        Returns:
            tuple[str|None, float]: Returns the name of the gesture and confidence.
                                    None if coordinates do not fit any Template.
        '''
        transformed_points = self.transform(points=points)
        result = self.recognizer.recognize(points=transformed_points)

        return result

    def transform(self, points: List[List[int]]) -> List[Point]:
        '''
        Transforms a list of coordinates to dollarpy Points
        '''
        transformed: List[Point] = []
        for point in points:
            transformed_point = Point(point[0], point[1])
            transformed.append(transformed_point)

        return transformed
