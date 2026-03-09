import logging

from weather.repositories import readings as repo

logger = logging.getLogger('weather')


def get_readings_list(sensor_name=None):
    """Return queryset of readings, optionally filtered by sensor name."""
    if sensor_name:
        logger.debug('Filtering readings by sensorName=%s', sensor_name)
    return repo.list_readings(sensor_name=sensor_name)


def create_reading(validated_data):
    """Create and return a new reading from validated data."""
    reading = repo.create_reading(validated_data)
    logger.info('Created WeatherReading id=%s sensor=%s', reading.id, reading.sensor_name)
    return reading
