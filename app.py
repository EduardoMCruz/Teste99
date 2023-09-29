from flask_openapi3 import OpenAPI, Info, Tag
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask import redirect

from model import Session, Especialidade
from schemas import *

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)


# tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
especialidade_tag = Tag(name="Especialidade", description="Cria, lista e remove especialidades da base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/especialidade', tags=[especialidade_tag],
          responses={"200": EspecialidadeViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_especialidade(form: EspecialidadeSchema):
    """Adiciona um novo especialidade à base de dados
    """
    especialidade = Especialidade(
        nome=form.nome)
    
    try:
        session = Session()
        session.add(especialidade)
        session.commit()
        return apresenta_especialidade(especialidade), 200

    except IntegrityError as e:
        error_msg = "Não foi possível cadastrar o especialidade, pois já existe um especialidade com esse código"
        print("erro: especialidade já cadastrado")
        return {"mesage": error_msg}, 409

    except Exception as e:
        error_msg = "Erro inesperado, o especialidade inserido não foi cadastrado"
        return {"mesage": error_msg}, 400

@app.get('/especialidades', tags=[especialidade_tag],
         responses={"200": ListagemEspecialidadesSchema, "404": ErrorSchema})
def get_especialidades():
    """Retorna uma listagem de especialidades cadastrados na base.
    """
    
    session = Session()
    especialidades = session.query(Especialidade).all()

    if not especialidades:
        return {"especialidades": []}, 200
    return apresenta_especialidades(especialidades), 200

@app.get('/especialidade', tags=[especialidade_tag],
            responses={"200": EspecialidadeViewSchema, "404": ErrorSchema})
def get_especialidade(query: EspecialidadeBuscaSchema):
    """Encontra um especialidade a partir do nome informado

    Retorna o especialidade.
    """
    nome = query.nome
    session = Session()
    especialidade = session.query(Especialidade).filter(Especialidade.nome == nome).first()
    if especialidade:
        return apresenta_especialidade(especialidade), 200
    error_msg = "Especialidade não encontrado"
    return {"mesage": error_msg}, 404
 
@app.delete('/especialidade', tags=[especialidade_tag],
            responses={"200": EspecialidadeDelSchema, "404": ErrorSchema})
def del_especialidade(query: EspecialidadeBuscaSchema):
    """Deleta um especialidade a partir do nome informado

    Retorna uma mensagem de confirmação da remoção.
    """
    nome = query.nome
    session = Session()
    count = session.query(Especialidade).filter(Especialidade.nome == nome).delete()
    session.commit()

    if count:
        return {"mesage": "Especialidade removido", "especialidade": nome}
    error_msg = "Especialidade não encontrado"
    return {"mesage": error_msg}, 404
    