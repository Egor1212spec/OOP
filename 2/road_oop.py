class Surface:
    def __init__(self, designation: str, max_velocity_kmh: int):
        self.designation = designation
        self.max_velocity_kmh = max_velocity_kmh

    def is_accessible(self, unit):
        return True

    def calculate_log(self, unit, distance):
        if not self.is_accessible(unit):
            return f"[X] {unit.label}: Доступ к '{self.designation}' закрыт."
        
        effective_speed = min(self.max_velocity_kmh, unit.speed_limit)
        hours = distance / effective_speed
        minutes = int(hours * 60)
        
        return (f"[✓] {unit.label} -> {self.designation} | "
                f"Дистанция: {distance} км | Время: {minutes} мин | "
                f"Ср. скорость: {effective_speed} км/ч")

class Autobahn(Surface):
    pass

class Downtown(Surface):
    def is_accessible(self, unit):
        return unit.type != 'heavy_cargo'

class RoughTerrain(Surface):
    def is_accessible(self, unit):
        return getattr(unit, 'all_terrain', False)

class FleetUnit:
    def __init__(self, label, speed_limit, unit_type='standard', all_terrain=False):
        self.label = label
        self.speed_limit = speed_limit
        self.type = unit_type
        self.all_terrain = all_terrain

class Sedan(FleetUnit):
    def __init__(self, name):
        super().__init__(name, 200, unit_type='passenger')

class Hauler(FleetUnit):
    def __init__(self, name):
        super().__init__(name, 85, unit_type='heavy_cargo')

class DirtBike(FleetUnit):
    def __init__(self, name, rally_mode=False):
        speed = 130 if rally_mode else 150
        super().__init__(name, speed, unit_type='moto', all_terrain=rally_mode)

if __name__ == "__main__":
    available_routes = [
        Autobahn("German Autobahn A1", 250),
        Downtown("Manhattan, 5th Avenue", 40),
        RoughTerrain("Rocky Mountains Pass", 60)
    ]

    transport_fleet = [
        Sedan("Tesla Model S"),
        Hauler("Scania R500"),
        DirtBike("KTM 450 Rally", rally_mode=True)
    ]

    test_distance = 25.0

    for route in available_routes:
        print(f"--- Тестирование маршрута: {route.designation} ---")
        for transport in transport_fleet:
            report = route.calculate_log(transport, test_distance)
            print(report)
        print("")