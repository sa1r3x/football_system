import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from xml.etree import ElementTree as ET

import yaml

from src.football_system.repositories import PlayerRepository


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "out"

# Схема экспорта: (поле из SQL-запроса, путь в итоговой структуре).
PLAYER_EXPORT_SCHEMA: Tuple[Tuple[str, str | Tuple[str, ...]], ...] = (
    ("id_players", "id_players"),
    ("fio", "fio"),
    ("number", "number"),
    ("position", "position"),
    ("team_name", ("team", "name")),
)

CSV_COLUMNS = [
    "_".join(target_path) if isinstance(target_path, tuple) else target_path
    for _, target_path in PLAYER_EXPORT_SCHEMA
]


class ExporterService:
    """Экспорт игроков вместе с командами в JSON, CSV, XML и YAML."""

    FILE_NAMES = {
        "json": "data.json",
        "csv": "data.csv",
        "xml": "data.xml",
        "yaml": "data.yaml",
    }

    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    def export_players(
        self,
        output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    ) -> Dict[str, Path]:
        """Создаёт папку экспорта и сохраняет четыре файла с данными."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        records = self._build_records(
            self.player_repo.get_all_with_team_name()
        )
        paths = {
            file_format: output_path / file_name
            for file_format, file_name in self.FILE_NAMES.items()
        }

        self._write_json(records, paths["json"])
        self._write_csv(records, paths["csv"])
        self._write_xml(records, paths["xml"])
        self._write_yaml(records, paths["yaml"])
        return paths

    def _build_records(
        self,
        rows: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Формирует единую структуру данных для всех форматов."""
        records = []

        for row in rows:
            record: Dict[str, Any] = {}
            for source_field, target_path in PLAYER_EXPORT_SCHEMA:
                value = row.get(source_field)

                if isinstance(target_path, tuple):
                    target = record
                    for part in target_path[:-1]:
                        target = target.setdefault(part, {})
                    target[target_path[-1]] = value
                else:
                    record[target_path] = value

            records.append(record)

        return records

    @staticmethod
    def _write_json(
        records: List[Dict[str, Any]],
        path: Path,
    ) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
            file.write("\n")

    @staticmethod
    def _write_csv(
        records: List[Dict[str, Any]],
        path: Path,
    ) -> None:
        rows = []

        for record in records:
            flat = {}
            for key, value in record.items():
                if isinstance(value, dict):
                    for nested_key, nested_value in value.items():
                        flat[f"{key}_{nested_key}"] = nested_value
                else:
                    flat[key] = value
            rows.append(flat)

        with open(path, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=CSV_COLUMNS,
                delimiter=";",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_xml(
        records: List[Dict[str, Any]],
        path: Path,
    ) -> None:
        root = ET.Element("players")

        for record in records:
            player = ET.SubElement(root, "player")

            for key, value in record.items():
                if isinstance(value, dict):
                    group = ET.SubElement(player, key)
                    for nested_key, nested_value in value.items():
                        child = ET.SubElement(group, nested_key)
                        child.text = (
                            "" if nested_value is None
                            else str(nested_value)
                        )
                else:
                    child = ET.SubElement(player, key)
                    child.text = "" if value is None else str(value)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _write_yaml(
        records: List[Dict[str, Any]],
        path: Path,
    ) -> None:
        with open(path, "w", encoding="utf-8") as file:
            yaml.dump(
                records,
                file,
                allow_unicode=True,
                sort_keys=False,
            )
