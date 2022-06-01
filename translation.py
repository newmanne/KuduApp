from modeltranslation.translator import translator, TranslationOptions
from agrotrade.models import UnitsDefinition, ProduceDefinition

'''Register models to translate with modeltranslation package'''

class UnitsDefinitionTranslationOptions(TranslationOptions):
    fields = ('code', 'unit_name',)

translator.register(UnitsDefinition, UnitsDefinitionTranslationOptions)

class ProduceDefinitionTranslationOptions(TranslationOptions):
    fields = ('display_name', )

translator.register(ProduceDefinition, ProduceDefinitionTranslationOptions)