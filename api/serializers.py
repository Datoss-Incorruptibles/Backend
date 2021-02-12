from rest_framework import serializers

from .models import Proceso, Cargo, OrganizacionPolitica, \
IndicadorCategoriaOrganizacion, IndicadorCategoria, Indicador, \
IndicadorCategoriaCandidato, Ubigeo, Candidato, CandidatoEstudio, \
CandidatoJudicial, CandidatoExperiencia, IndicadorCategoriaCandidato, \
CandidatoIngreso, CandidatoInmueble, CandidatoMueble, CandidatoMedio, \
OrganizacionPlan, OrganizacionPlanDetalle 

class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = ('nombre', 'estado')


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = ('cargo', 'estado')


class UbigeoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ubigeo', read_only=True)
    class Meta:
        model = Ubigeo
        fields = ('id','region','distrito_electoral')



class OrgPolComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizacionPolitica
        fields = ('id','nombre', 'estado','jne_idorganizacionpolitica')


        
class IndicadorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Indicador
        fields = ('nombre','alerta','estado')


class IndicadorCategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndicadorCategoria
        fields = ('indicador','nombre','alerta','estado','order')

class IndicadorCategoriaOrganizacionSerializer(serializers.ModelSerializer):
    indicador_categoria_nombre = serializers.CharField(source='indicador_categoria', read_only=True)
    indicador_titulo = serializers.CharField(source='indicador.titulo', read_only=True)
    indicador_ubicacion = serializers.IntegerField(source='indicador.ubicacion', read_only=True)
    indicador_alerta = serializers.IntegerField(source='indicador.alerta', read_only=True)

    class Meta:
        model = IndicadorCategoriaOrganizacion
        fields = ('indicador_categoria_nombre','indicador_categoria','indicador',
                'cantidad','porcentaje','alerta','indicador_titulo','indicador_ubicacion','indicador_alerta')

class IndicadorCategoriaCandidatoSerializer(serializers.ModelSerializer):
    indicador_categoria_nombre = serializers.CharField(source='indicador_categoria', read_only=True)
    indicador_nombre = serializers.CharField(source='indicador', read_only=True)
    nivel = serializers.IntegerField(source='indicador_categoria.order', read_only=True)
    class Meta:
        model = IndicadorCategoriaCandidato
        fields = ('indicador_categoria_nombre','indicador_categoria','indicador_nombre','indicador',
                'cantidad','porcentaje','alerta','estado','nivel')


class OrganizacionPoliticaSerializer(serializers.ModelSerializer):
    indicadorescategoriaorg = IndicadorCategoriaOrganizacionSerializer(many=True, read_only=True)
    sentencias = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrganizacionPolitica
        fields = ('id','nombre','fundacion_fecha', 'estado','descripcion','ruta_archivo',
                'jne_idorganizacionpolitica','indicadorescategoriaorg','sentencias')

class OrganizacionPoliticaDetalleSerializer(serializers.ModelSerializer):
    indicadorescategoriaorg = IndicadorCategoriaOrganizacionSerializer(many=True, read_only=True)
    plangobierno = serializers.SerializerMethodField()

    def get_plangobierno(self, obj):
        plan = OrganizacionPlan.objects.get(organizacion_politica_id=obj.pk, tipo_eleccion=1)
        plan_detalle = OrganizacionPlanDetalle.objects.filter(plan_id=plan.pk).order_by('dimension_id')
        if not plan_detalle:
            return None
        return PlanGobiernoSerializer(plan_detalle, many=True).data

    class Meta:
        model = OrganizacionPolitica
        fields = ('id','nombre','fundacion_fecha', 'estado','descripcion','ruta_archivo',
                'jne_idorganizacionpolitica','indicadorescategoriaorg','plangobierno')

class PlanGobiernoSerializer(serializers.Serializer):
    problema = serializers.CharField()
    objetivo = serializers.CharField()
    meta = serializers.CharField()
    indicador = serializers.CharField()
    dimension_id = serializers.IntegerField()
    criterio_id = serializers.IntegerField(source="plan_criterio_id")
    criterio = serializers.CharField(source="plan_criterio.nombre")


class CandidatoSerializer(serializers.ModelSerializer):

    # candidatos by org pol and cargo pol 
    indicadores = serializers.SerializerMethodField()

    def get_indicadores(self, obj):
        indicadores = IndicadorCategoriaCandidato.objects.filter(candidato=obj.pk, estado=1).order_by('indicador','indicador_categoria')
        if not indicadores:
            return None
        return IndicadoresCandidatoSerializer(indicadores, many=True, read_only=True).data

    class Meta:
        model = Candidato
        fields = ('id', 'jne_idcandidato','jne_idhojavida','jne_estado_lista', 'jne_estado_expediente','jne_estado_hojavida','jne_posicion','jne_organizacion_politica','cargo_id',
        'proceso_id','proceso_id','organizacion_politica_id','organizacion_politica_logo', 'documento_identidad','apellido_paterno','apellido_materno','nombres',
        'profesion','nivel_estudio_id_max','region', 'distrito_electoral','ubigeo_postula','ruta_archivo','fecha_registro','fecha_modificacion','indicadores')


class IndicadoresCandidatoSerializer(serializers.Serializer):

    indicador_categoria = serializers.CharField(source="indicador_categoria.nombre")
    indicador_categoria_id = serializers.IntegerField()
    indicador = serializers.CharField(source="indicador.titulo")
    indicador_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    porcentaje = serializers.FloatField()
    alerta = serializers.IntegerField()
    estado = serializers.IntegerField()


class CandidatoDetailSerializer(serializers.ModelSerializer):
    indicadores_categoria_candidato = IndicadorCategoriaCandidatoSerializer(many=True, read_only=True)
    estudios = serializers.SerializerMethodField()
    sentencias = serializers.SerializerMethodField()
    experiencialaboral = serializers.SerializerMethodField()
    experienciapolitica = serializers.SerializerMethodField()
    experienciapartido = serializers.SerializerMethodField()
    ingresos = serializers.SerializerMethodField()
    inmuebles = serializers.SerializerMethodField()
    muebles = serializers.SerializerMethodField()
    medios = serializers.SerializerMethodField()

    def get_sentencias(self, obj):
        candidato_sentencias = CandidatoJudicial.objects.filter(jne_idhojavida=obj.jne_idhojavida).order_by('tipo_proceso')
        if not candidato_sentencias:
            return None
        return CandidatoJudicialSerializer(candidato_sentencias, many=True).data

    def get_estudios(self, obj):
        candidato_estudios = CandidatoEstudio.objects.filter(jne_idhojavida=obj.jne_idhojavida).order_by('-nivel_estudio_id')
        if not candidato_estudios:
            return None
        return CandidatoEstudioSerializer(candidato_estudios, many=True).data

    def get_experiencialaboral(self, obj):
        candidato_exp_laboral = CandidatoExperiencia.objects.filter(jne_idhojavida=obj.jne_idhojavida, tipo=1).order_by('-anio_trabajo_desde')
        if not candidato_exp_laboral:
            return None
        return CandidatoExperienciaSerializer(candidato_exp_laboral, many=True).data

    def get_experienciapolitica(self, obj):
        candidato_exp_politica = CandidatoExperiencia.objects.filter(jne_idhojavida=obj.jne_idhojavida, tipo=3).order_by('-anio_trabajo_desde')
        if not candidato_exp_politica:
            return None
        return CandidatoExperienciaSerializer(candidato_exp_politica, many=True).data

    def get_experienciapartido(self, obj):
        candidato_exp_partido = CandidatoExperiencia.objects.filter(jne_idhojavida=obj.jne_idhojavida, tipo=2).order_by('-anio_trabajo_desde')
        if not candidato_exp_partido:
            return None
        return CandidatoExperienciaSerializer(candidato_exp_partido, many=True).data

    def get_ingresos(self, obj):
        candidato_ingresos = CandidatoIngreso.objects.filter(jne_idhojavida=obj.jne_idhojavida)
        if not candidato_ingresos:
            return None
        return CandidatoIngresoSerializer(candidato_ingresos, many=True).data
       

    def get_inmuebles(self, obj):
        candidato_inmuebles = CandidatoInmueble.objects.filter(jne_idhojavida=obj.jne_idhojavida).order_by('order')
        if not candidato_inmuebles:
            return None
        return CandidatoInmuebleSerializer(candidato_inmuebles, many=True).data
       

    def get_muebles(self, obj):
        candidato_muebles = CandidatoMueble.objects.filter(jne_idhojavida=obj.jne_idhojavida).order_by('order')
        if not candidato_muebles:
            return None
        return CandidatoMuebleSerializer(candidato_muebles, many=True).data
    

    def get_medios(self, obj):
        candidato_medio = CandidatoMedio.objects.filter(jne_idhojavida=obj.jne_idhojavida).order_by('-fecha')
        if not candidato_medio:
            return None
        return CandidatoMedioSerializer(candidato_medio, many=True).data
    
    class Meta:
        model = Candidato
        fields = ('id', 'jne_idcandidato','jne_idhojavida','jne_estado_lista', 'jne_estado_expediente',
                'jne_estado_hojavida','jne_posicion','jne_organizacion_politica','cargo_id',
                'proceso_id','proceso_id','organizacion_politica_id','organizacion_politica_logo',
                'documento_identidad','apellido_paterno','apellido_materno','nombres',
                'profesion','nivel_estudio_id_max','region', 'distrito_electoral','ubigeo_postula',
                'ruta_archivo','fecha_nacimiento','fecha_registro','fecha_modificacion',
                'indicadores_categoria_candidato','sentencias','estudios','experiencialaboral',
                'experienciapolitica','experienciapartido','ingresos','inmuebles','muebles','medios')


class CandidatoEstudioSerializer(serializers.Serializer):
    grado = serializers.CharField()
    institucion = serializers.CharField()
    estudio = serializers.CharField()
    anio_bachiller = serializers.CharField()
    anio_titulo = serializers.CharField()
    nivel_estudio_estado = serializers.CharField()

class CandidatoJudicialSerializer(serializers.Serializer):
    tipo_proceso = serializers.CharField()
    sentencia = serializers.CharField()
    nro_expediente = serializers.CharField()
    fallo = serializers.CharField()
    cumple_fallo = serializers.CharField()
    tipo_proceso = serializers.CharField()


class CandidatoExperienciaSerializer(serializers.Serializer):
    centro_trabajo = serializers.CharField()
    ocupacion_profesion = serializers.CharField()
    anio_trabajo_desde = serializers.CharField()
    anio_trabajo_hasta = serializers.CharField()


class CandidatoIngresoSerializer(serializers.Serializer):

    renta_bruta_privado = serializers.FloatField()
    renta_bruta_publico = serializers.FloatField()
    renta_individual_privado = serializers.FloatField()
    renta_individual_publico = serializers.FloatField()
    otros_ingresos_privado = serializers.FloatField()
    otros_ingresos_publico = serializers.FloatField()
    anio_ingresos = serializers.IntegerField()


class CandidatoInmuebleSerializer(serializers.Serializer):
    direccion = serializers.CharField()
    valor = serializers.FloatField()
    order = serializers.IntegerField()
    comentario = serializers.CharField()
    partida_sunarp = serializers.CharField()
    tipo = serializers.CharField()

class CandidatoMuebleSerializer(serializers.Serializer):
    caracteristica = serializers.CharField()
    comentario = serializers.CharField()
    marca =  serializers.CharField()
    order = serializers.IntegerField()
    modelo = serializers.CharField()
    placa = serializers.CharField()
    valor = serializers.FloatField()
    vehiculo = serializers.CharField()


class CandidatoMedioSerializer(serializers.Serializer):
    titulo = serializers.CharField()
    url = serializers.URLField()
    tipo = serializers.CharField()
    fecha = serializers.DateField()
    medio = serializers.CharField()