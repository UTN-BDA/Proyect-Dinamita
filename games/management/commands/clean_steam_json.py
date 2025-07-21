# management/commands/clean_steam_json.py
from django.core.management.base import BaseCommand, CommandError
import json
from dateutil import parser
import pandas as pd
from tqdm import tqdm

class Command(BaseCommand):
    help = ('Limpia y normaliza un archivo JSON de datos Steam y exporta '
            'un objeto JSON con claves por app_id y valores limpios.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--input', type=str, required=True,
            help='Ruta al archivo JSON crudo de entrada'
        )
        parser.add_argument(
            '--output', type=str, required=True,
            help='Ruta al archivo JSON limpio de salida'
        )

    def handle(self, *args, **options):
        input_path = options['input']
        output_path = options['output']
        try:
            self.stdout.write('Cargando JSON...')
            df = self.load_json(input_path)

            self.stdout.write('Normalizando fechas a DD/MM/YYYY...')
            df = self.normalize_dates(df)

            self.stdout.write('Convirtiendo price a float...')
            df = self.ensure_price_float(df)

            self.stdout.write('Limpiando campos de texto...')
            df = self.clean_text_fields(df, [
                'detailed_description', 'about_the_game', 'short_description'
            ])

            self.stdout.write('Eliminando columnas no deseadas...')
            dropcols = ['header_image', 'screenshots', 'movies', 'peak_ccu', 'release_date_std']
            df = df.drop(columns=[c for c in dropcols if c in df.columns])

            self.stdout.write('Convirtiendo OS a booleanos...')
            for col in ['windows', 'mac', 'linux']:
                if col in df.columns:
                    df[col] = df[col].astype(bool)

            self.stdout.write('Reformateando estimated_owners...')
            if 'estimated_owners' in df.columns:
                df['estimated_owners'] = df['estimated_owners'] \
                    .astype(str) \
                    .str.replace(r"\s*-\s*", ',', regex=True)

            self.stdout.write('Descartando cols >80% vacíos...')
            frac_empty = df.isna().mean()
            sparse = frac_empty[frac_empty >= 0.8].index.tolist()
            df = df.drop(columns=sparse)

            self.stdout.write('Exportando JSON objeto...')
            records = df.to_dict(orient='records')
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write('{' + '\n')
                for i, rec in enumerate(records):
                    app_id = rec.pop('app_id')
                    if 'release_date_dmy' in rec:
                        rec['release_date'] = rec.pop('release_date_dmy')
                    # Dump value and unescape slashes
                    value = json.dumps(rec, ensure_ascii=False).replace('\\/', '/')
                    comma = ',' if i < len(records) - 1 else ''
                    out.write(f'    "{app_id}": {value}{comma}\n')
                out.write('}' + '\n')

            self.stdout.write(self.style.SUCCESS(
                f'JSON limpio guardado en {output_path}'
            ))
        except Exception as e:
            raise CommandError(f'Error al procesar JSON: {e}')

    def load_json(self, path: str) -> pd.DataFrame:
        # Carga JSON donde keys=app_id y values=dict
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        records = []
        for app_id, data in tqdm(raw.items(), desc='Procesando apps'):
            data['app_id'] = app_id
            records.append(data)
        return pd.DataFrame(records)

    def normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'release_date' in df.columns:
            df['release_date'] = df['release_date'] \
                .apply(parser.parse) \
                .dt.strftime('%d/%m/%Y')
        return df

    def ensure_price_float(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        return df

    def clean_text_fields(self, df: pd.DataFrame, fields: list) -> pd.DataFrame:
        for f in fields:
            if f in df.columns:
                df[f] = df[f] \
                    .astype(str) \
                    .str.strip() \
                    .replace({'': None})
        return df

    def drop_sparse(self, df: pd.DataFrame, threshold: float) -> pd.DataFrame:
        frac_empty = df.isna().mean()
        drop_cols = frac_empty[frac_empty >= threshold].index.tolist()
        return df.drop(columns=drop_cols)

    def transform_estimated_owners(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'estimated_owners' in df.columns:
            df['estimated_owners'] = df['estimated_owners'] \
                .astype(str) \
                .str.replace(r"\s*-\s*", ',', regex=True)
        return df

    def clean_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.normalize_dates(df)
        df = self.ensure_price_float(df)
        df = self.clean_text_fields(df, ['detailed_description','about_the_game','short_description'])
        df = df.drop(columns=[c for c in ['header_image','screenshots','movies','peak_ccu','release_date_std'] if c in df.columns])
        for col in ['windows','mac','linux']:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        df = self.transform_estimated_owners(df)
        df = self.drop_sparse(df, 0.8)
        return df