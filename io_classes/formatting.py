from typing import Iterable, Mapping


class Format:
    """Create human-readable strings for reports."""

    @staticmethod
    def record(record: Mapping[str, object]) -> str:
        report_type = str(
            record.get("report_type", record.get("type", "unknown"))
        ).title()
        case_id = str(record.get("case_id", "unknown"))
        status = str(record.get("status", "Unknown"))
        category = str(record.get("category", "unknown")).title()
        identifying_features = record.get(
            "identifying_features", "No identifying features"
        )
        image_path = str(
            record.get(
                "image_filename",
                record.get("image_path", record.get("image", "No image")),
            )
        )
        occurrence_date = str(
            record.get("date", record.get("occurrence_date", "Unknown date"))
        )
        features = (
            ", ".join(identifying_features)
            if isinstance(identifying_features, list)
            else identifying_features
        )
        return (
            f"{report_type} report\n"
            f"  Case ID: {case_id}\n"
            f"  Status: {status}\n"
            f"  Category: {category}\n"
            f"  Identifying Features: {features}\n"
            f"  Date: {occurrence_date}\n"
            f"  Image: {image_path}"
        )

    @classmethod
    def records(cls, records: Iterable[Mapping[str, object]]) -> str:
        record_list = list(records)
        if not record_list:
            return "No reports found."
        return "\n\n".join(
            f"{number}. {cls.record(record)}"
            for number, record in enumerate(record_list, start=1)
        )
