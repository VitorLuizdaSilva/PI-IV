from django.core.management.base import BaseCommand

from produtividade.views import fechar_meses_anteriores


class Command(BaseCommand):
    help = "Fecha os meses anteriores e salva seus indicadores."

    def handle(self, *args, **options):
        fechar_meses_anteriores()

        self.stdout.write(
            self.style.SUCCESS(
                "Verificação dos fechamentos mensais concluída."
            )
        )