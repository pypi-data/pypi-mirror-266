from pythonjsonlogger.jsonlogger import JsonFormatter, merge_record_extra

bind = ["0.0.0.0:8000"]
forwarded_allow_ips = "*"
workers = 5


# Based on https://stackoverflow.com/a/70511781
class GunicornJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        """
        This method allows us to inject gunicorn's args as fields for the formatter
        """
        super(GunicornJsonFormatter, self).add_fields(log_record, record, message_dict)
        for field in self._required_fields:
            if field in self.rename_fields:
                log_record[self.rename_fields[field]] = record.args.get(field)  # type: ignore
            else:
                log_record[field] = record.args.get(field)  # type: ignore


logconfig_dict = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "pyquocca.gunicorn.GunicornJsonFormatter",
            "format": "%(M)s %(t)s %(r)s %(s)s %(p)s %(a)s %({host}i)s %({x-mtls-full-name}i)s %({x-forwarded-for}i)s %({x-mtls-username}i)s %({x-mtls-staff}i)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "rename_fields": {
                "M": "duration",
                "a": "user_agent",
                "t": "time",
                "{host}i": "host",
                "{x-forwarded-for}i": "ip",
                "s": "status",
                "r": "request",
                "p": "process_id",
                "{x-mtls-full-name}i": "full_name",
                "{x-mtls-username}i": "user",
                "{x-mtls-staff}i": "is_staff",
                "{x-mtls-impersonated-by}i": "impersonated_by",
            },
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {"gunicorn.access": {"level": "INFO", "handlers": ["console"]}},
}
