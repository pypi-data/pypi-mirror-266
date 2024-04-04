import json
import os
from pathlib import Path

import pytest
import requests
from dirty_equals import HasLen, HasAttributes, IsList, IsPartialDict
from pymultirole_plugins.v1.schema import Document, DocumentList

from pyprocessors_openai_completion.openai_completion import (
    OpenAICompletionProcessor,
    OpenAICompletionParameters,
    OpenAIModel,
    flatten_document, OpenAIFunction, AzureOpenAICompletionProcessor,
    DeepInfraOpenAICompletionProcessor, AzureOpenAICompletionParameters,
    CHAT_GPT_MODEL_ENUM, DeepInfraOpenAICompletionParameters
)


def test_openai_completion_basic():
    model = OpenAICompletionProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == OpenAICompletionParameters

    model = AzureOpenAICompletionProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == AzureOpenAICompletionParameters

    model = DeepInfraOpenAICompletionProcessor.get_model()
    model_class = model.construct().__class__
    assert model_class == DeepInfraOpenAICompletionParameters


def test_flatten_doc():
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/complexdoc.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        doc = Document(**jdoc)
        flatten = flatten_document(doc)
        assert flatten == IsPartialDict(
            text=doc.text,
            title=doc.title,
            metadata_foo=doc.metadata["foo"],
            altTexts_0_name=doc.altTexts[0].name,
        )


JINJA_PROMPTS = {
    "preserve_entities": """Generates several variants of the following context while preserving the given named entities. Each named entity must be between square brackets using the notation [label:entity].
    Context: {{ doc.text }}
    {%- set entities=[] -%}
    {%- for a in doc.annotations -%}
      {%- do entities.append('[' + a.label + ':' + a.text + ']') -%}
    {%- endfor %}
    Given named entities using the notation [label:entity]: {{ entities|join(', ') }}
    Output language: {{ doc.metadata['language'] }}
    Output format: bullet list""",
    "substitute_entities": """Generates several variants of the following context while substituting the given named entities by semantically similar named entities with the same label, for each variant insert the new named entities between square brackets using the notation [label:entity].
    Context: {{ doc.text }}
    {%- set entities=[] -%}
    {%- for a in doc.annotations -%}
      {%- do entities.append('[' + a.label + ':' + a.text + ']') -%}
    {%- endfor %}
    Given named entities using the notation [label:entity]: {{ entities|join(', ') }}
    Output language: {{ doc.metadata['language'] }}
    Output format: bullet list""",
}


@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("typed_prompt", [p for p in JINJA_PROMPTS.items()])
def test_jinja_doc(typed_prompt):
    type = typed_prompt[0]
    prompt = typed_prompt[1]
    parameters = OpenAICompletionParameters(
        max_tokens=3000,
        completion_altText=type,
        prompt=prompt,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/jinjadocs.json",
    )
    with source.open("r") as fin:
        jdocs = json.load(fin)
        docs = [Document(**jdoc) for jdoc in jdocs]
        docs = processor.process(docs, parameters)
        assert docs == HasLen(6)
        sum_file = testdir / f"data/jinjadocs_{type}.json"
        dl = DocumentList(__root__=docs)
        with sum_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
    # noqa: E501


def chunks(seq, size=1000):  # noqa
    return (seq[pos: pos + size] for pos in range(0, len(seq), size))


@pytest.mark.skip(reason="Not a test")
def test_semeval_docs():
    start_at = 32
    parameters = OpenAICompletionParameters(
        max_tokens=3000,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/semeval_fa_da.json",
    )
    with source.open("r") as fin:
        jdocs = json.load(fin)
        for i, chunk in enumerate(chunks(jdocs, 10)):
            if i >= start_at:
                docs = [Document(**jdoc) for jdoc in chunk]
                for type, prompt in JINJA_PROMPTS.items():
                    parameters.prompt = prompt
                    parameters.completion_altText = type
                    docs = processor.process(docs, parameters)
                    # assert docs == HasLen(6)
                    sum_file = testdir / f"data/semeval_fa_da_{type}_{i}.json"
                    dl = DocumentList(__root__=docs)
                    with sum_file.open("w") as fout:
                        print(
                            dl.json(exclude_none=True, exclude_unset=True, indent=2),
                            file=fout,
                        )


@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("model", [m for m in CHAT_GPT_MODEL_ENUM])
def test_openai_prompt(model):
    parameters = OpenAICompletionParameters(
        model=model, max_tokens=120, completion_altText="completion"
    )
    processor = OpenAICompletionProcessor()
    docs_with_prompts = [
        (
            Document(
                identifier="1",
                text="séisme de magnitude 7,8 a frappé la Turquie",
                metadata={"language": "fr"},
            ),
            "Peux tu écrire un article de presse concernant: $text",
        ),
        (
            Document(
                identifier="2",
                text="j'habite dans une maison",
                metadata={"language": "fr"},
            ),
            "Peux tu me donner des phrases similaires à: $text",
        ),
        (
            Document(
                identifier="3",
                text="il est né le 21 janvier 2000",
                metadata={"language": "fr"},
            ),
            "Peux tu me donner des phrases similaires en changeant le format de date à: $text",
        ),
        (
            Document(
                identifier="4",
                text="""Un nuage de fumée juste après l’explosion, le 1er juin 2019.
                Une déflagration dans une importante usine d’explosifs du centre de la Russie a fait au moins 79 blessés samedi 1er juin.
                L’explosion a eu lieu dans l’usine Kristall à Dzerzhinsk, une ville située à environ 400 kilomètres à l’est de Moscou, dans la région de Nijni-Novgorod.
                « Il y a eu une explosion technique dans l’un des ateliers, suivie d’un incendie qui s’est propagé sur une centaine de mètres carrés », a expliqué un porte-parole des services d’urgence.
                Des images circulant sur les réseaux sociaux montraient un énorme nuage de fumée après l’explosion.
                Cinq bâtiments de l’usine et près de 180 bâtiments résidentiels ont été endommagés par l’explosion, selon les autorités municipales. Une enquête pour de potentielles violations des normes de sécurité a été ouverte.
                Fragments de shrapnel Les blessés ont été soignés après avoir été atteints par des fragments issus de l’explosion, a précisé une porte-parole des autorités sanitaires citée par Interfax.
                « Nous parlons de blessures par shrapnel d’une gravité moyenne et modérée », a-t-elle précisé.
                Selon des représentants de Kristall, cinq personnes travaillaient dans la zone où s’est produite l’explosion. Elles ont pu être évacuées en sécurité.
                Les pompiers locaux ont rapporté n’avoir aucune information sur des personnes qui se trouveraient encore dans l’usine.
                """,
                metadata={"language": "fr"},
            ),
            "Peux résumer dans un style journalistique le texte suivant: $text",
        ),
        (
            Document(
                identifier="5",
                text="Paris is the capital of France and Emmanuel Macron is the president of the French Republic.",
                metadata={"language": "en"},
            ),
            "Can you find the names of people, organizations and locations in the following text:\n\n $text",
        ),
    ]
    docs = []
    for doc, prompt in docs_with_prompts:
        parameters.prompt = prompt
        doc0 = processor.process([doc], parameters)[0]
        docs.append(doc0)
        assert doc0.altTexts == IsList(
            HasAttributes(name=parameters.completion_altText)
        )
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / f"en_{model.value}.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


# noqa: E501
@pytest.mark.skip(reason="Not a test")
@pytest.mark.parametrize("model", [m for m in CHAT_GPT_MODEL_ENUM])
def test_openai_text(model):
    parameters = OpenAICompletionParameters(
        model=model,
        system_prompt="Tu es un journaliste",
        max_tokens=120,
        best_of=3,
        n=3,
        completion_altText="completion",
    )
    processor = OpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Peux tu écrire un article de presse concernant: séisme de magnitude 7,8 a frappé la Turquie",
            metadata={"language": "fr"},
        ),
        Document(
            identifier="2",
            text="Peux tu me donner des phrases similaires à: j'habite dans une maison",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    for doc in docs:
        assert doc.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / f"fr_{model.value}.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


# noqa: E501
@pytest.mark.skip(reason="Not a test")
def test_q_and_a():
    prompt = """Répondre à la question en utilisant les segments suivants et en citant les références.
    Question: {{ doc.altTexts[0].text }}
    Segments: {{ doc.text }}"""

    parameters = OpenAICompletionParameters(
        max_tokens=2000,
        completion_altText=None,
        prompt=prompt,
    )
    processor = OpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/question_segments.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        docs = [Document(**jdoc)]
        docs = processor.process(docs, parameters)
        assert docs == HasLen(1)
        sum_file = testdir / "data/question_segments_answer.json"
        dl = DocumentList(__root__=docs)
        with sum_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
    # noqa: E501


@pytest.mark.skip(reason="Not a test")
def test_azure_endpoint():
    parameters = AzureOpenAICompletionParameters(
        system_prompt="Tu es un journaliste",
        max_tokens=1000,
        best_of=3,
        n=3,
        completion_altText="completion",
    )
    processor = AzureOpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Peux tu écrire un article de presse concernant: séisme de magnitude 7,8 a frappé la Turquie",
            metadata={"language": "fr"},
        ),
        Document(
            identifier="2",
            text="Peux tu me donner des phrases similaires à: j'habite dans une maison",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    for doc in docs:
        assert doc.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / "fr_azure_gpt_4.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        fout.write(dl.json(exclude_none=True, exclude_unset=True, indent=2))


@pytest.mark.skip(reason="Not a test")
def test_deepinfra_endpoint():
    parameters = DeepInfraOpenAICompletionParameters(
        max_tokens=100,
        completion_altText="completion",
    )
    processor = DeepInfraOpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Peux tu écrire un article de presse concernant: séisme de magnitude 7,8 a frappé la Turquie",
            metadata={"language": "fr"},
        ),
        Document(
            identifier="2",
            text="Peux tu me donner des phrases similaires à: j'habite dans une maison",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(2)
    for doc in docs:
        assert doc.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
    testdir = Path(__file__).parent / "data"
    sum_file = testdir / "fr_llama2.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        fout.write(dl.json(exclude_none=True, exclude_unset=True, indent=2))


@pytest.mark.skip(reason="Not a test")
def test_direct_deepinfra():
    PROMPT = """[INST]Answer the question in french using the given segments of a long document and making references of those segments ["SEGMENT"] with the segment number. 
Be short and precise as possible. If you don't know the answer, just say that you don't know. Don't try to make up an answer.
Question: Est-il prévu des congés rémunérés pour les femmes souffrant de douleurs menstruelles ?

SEGMENTS:
1. À l’heure où certaines entreprises ou même certaines collectivités prévoient des congés rémunérés pour les femmes souffrant de douleurs menstruelles importantes ou d’endométriose, une proposition de loi a été déposée au Sénat en ce sens le 18 avril 2023 par une sénatrice socialiste et plusieurs de ses collègues. Les femmes concernées pourraient faire l’objet d’un arrêt de travail ou encore télétravailler, sous certaines conditions. La proposition de loi prévoit aussi un congé payé pour les femmes (et leur conjoint) ayant subi une fausse couche.

2. La proposition de loi prévoit de créer un arrêt de travail indemnisé pour les femmes souffrant de dysménorrhée (règles douloureuses) ou d’endométriose (maladie gynécologique inflammatoire et chronique). Prescrit par un médecin ou une sage-femme, cet arrêt maladie autoriserait la salariée à interrompre son travail chaque fois qu’elle se trouverait dans l’incapacité physique de travailler, pour une durée ne pouvant excéder 2 jours par mois sur une période de 3 mois. Les IJSS, versées sans délai de carence, se calculeraient selon des règles dérogatoires favorables à la salariée.  Dans l’objectif d’éviter un arrêt de travail, la proposition de loi vise aussi à favoriser la possibilité de télétravail pour les femmes souffrant de règles douloureuses et invalidantes, via l'accord collectif ou la charte sur le télétravail lorsqu'il en existe un.    Enfin, le texte propose de créer sur justification, pour les femmes affectées par une interruption spontanée de grossesse, un congé rémunéré de 5 jours ouvrables. Le conjoint, concubin ou partenaire pacsé de la salariée aurait aussi droit à ce congé.    Reste à voir si cette 2e proposition de loi, déposée le 18 avril par une sénatrice socialiste et plusieurs de ses collègues, connaîtra un sort aussi favorable que la première.

3. Maternité, paternité, adoption, femmes enceintes dispensées de travail - L’employeur doit compléter une attestation de salaire lorsque le congé de maternité* débute (c. séc. soc. art. R. 331-5, renvoyant à c. séc. soc. art. R. 323-10).      Le même document est à compléter en cas de congé d’adoption*, de congé de paternité et d’accueil de l’enfant* ou, dans le cadre de la protection de la maternité, pour les femmes travaillant de nuit ou occupant des postes à risques dispensées de travail en raison d’une impossibilité de reclassement sur un poste de jour ou sans risques .      Il s’agit de la même attestation que celle prévue pour les arrêts maladie.

4. Grossesse pathologique liée au distilbène - Le distilbène (ou diéthylstilbestrol) prescrit il y a plusieurs années entraîne des grossesses pathologiques chez les femmes qui y ont été exposées in utero.      Les femmes chez lesquelles il est reconnu que la grossesse pathologique est liée à l’exposition in utero au distilbène bénéficient d’un congé de maternité à compter du premier jour de leur arrêt de travail (loi 2004-1370 du 20 décembre 2004, art. 32         ; décret 2006-773 du 30 juin 2006, JO 2 juillet).

5. Enfant né sans vie - L'indemnité journalière de maternité est allouée même si l'enfant n'est pas né vivant au terme de 22 semaines d'aménorrhée (c. séc. soc. art. R. 331-5). Pathologie liée au Distilbène - Bien que ce médicament ne soit plus prescrit, le Distilbène (ou diéthyltilbestrol) peut entraîner des grossesses pathologiques pour les femmes qui y ont été exposées in utero. Les femmes dont il est reconnu que la grossesse pathologique est liée à l’exposition in utero au Distilbène bénéficient d’un congé de maternité à compter du premier jour de leur arrêt de travail (loi 2004-1370 du 20 décembre 2004, art. 32, JO du 21). Ces femmes peuvent prétendre à l’IJSS de maternité dès le début de leur congé de maternité si elles remplissent les conditions d’ouverture du droit au congé légal de maternité (décret 2006-773 du 30 juin 2006, JO 2 juillet).

6. Possibilité de télétravailler pour les femmes souffrant de règles douloureuses Dans l’objectif d’éviter un arrêt de travail pour douleurs menstruelles, la proposition de loi vise à favoriser la possibilité de télétravail aux femmes souffrant de dysménorrhée (proposition de loi, art. 4).   À cet égard, l'accord collectif ou la charte sur le télétravail existant dans l’entreprise devrait préciser les modalités d’accès des salariées souffrant de règles douloureuses et invalidantes à une organisation en télétravail.    En toute logique, il ressort de l’exposé des motifs que cela ne viserait que les femmes dont l’activité professionnelle est compatible avec l’exercice du télétravail.      À noter : en dehors d’un accord ou d’une charte sur le télétravail, il est toujours possible à l’employeur et au salarié de convenir d’un recours au télétravail formalisé par tout moyen (c. trav. art. L. 1222-9).Une proposition de loi en faveur des femmes souffrant de douleurs menstruelles, d’endométriose, ou ayant subi une fausse couche
    [/INST]"""
    api_key = os.getenv("DEEPINFRA_OPENAI_API_KEY")
    deploy_infer_url = "https://api.deepinfra.com/v1/inference/meta-llama/Llama-2-70b-chat-hf"
    response = requests.post(deploy_infer_url, json={
        "input": PROMPT,
        "max_new_tokens": 4096,
        "temperature": 0.2
    },
                             headers={'Content-Type': "application/json",
                                      'Authorization': f"Bearer {api_key}"})
    if response.ok:
        result = response.json()
        texts = "\n".join([r['generated_text'] for r in result['results']])
        assert len(texts) > 0


# noqa: E501

@pytest.mark.skip(reason="Not a test")
def test_function_call_ner():
    candidate_labels = {
        'resource': 'RESOURCE',
        'organization': 'ORGANIZATION',
        'group': 'GROUP',
        'person': 'PERSON',
        'event': 'EVENT',
        'function': 'FUNCTION',
        'time': 'TIME'
    }

    prompt = """Vous êtes un système expert de reconnaissance d'entités nommées.
Votre tâche consiste à accepter un paragraphe en entrée et à en extraire les entités nommées.
Les entités doivent avoir l'une des étiquettes suivantes : ORGANIZATION, GROUP, RESOURCE, TIME, MILITARY_UNIT, UNKNOWN, LOCATION, SITE, FUNCTION, PERSON, EQUIPMENT, ID et EVENT

Consignes générales:
Parfois, pour reconnaître un événement, un lieu, ou tout autre type d'entité, l’annotateur doit faire appel à sa connaissance du monde et au contexte de la phrase.
On cherche à conserver autant que possible la structure syntaxique pour les entités ORGANIZATION, MILITARY_UNIT, GROUP, EQUIPMENT, RESSOURCE, TIME, LOCATION et SITE. En effet, on annote notamment les articles et les adjectifs qui se rapportent aux noms annotés, c'est-à-dire qu'on annote tout le groupe nominal. On n'inclut cependant pas dans l’annotation une phrase subordonnée (voir exemple 1).

Pour les entités UNKNOWN et FUNCTION, on conserve la structure syntaxique
comme pour les entités ci-dessus mais sans inclure le nom propre de la personne en question. S'il apparaît juste après, celui-ci est annoté en PERSON.

L'annotation des entités PERSON et ID se limite aux noms propres des personnes, ou au corps de l'identifiant.

Pour ce qui est des prépositions introduisant l'entité, on ne souhaite les garder que dans les cas de TIME, LOCATION et SITE. Attention, il faut bien distinguer la préposition des (de+les) de l'article indéfini des (pluriel de un)

On sépare les entités dont les mentions sont séparées par une virgule (ou tout autre forme d'énumération) dans le texte.
On peut être amené à couper sur une apostrophe.
On n'annote pas les anaphores et les références (il, eux, ces dernières...).

Dans «C'est le Général qui a donné l'ordre.»
On annote «le Général»; la subordonnée introduite par qui n'est pas incluse dans l'annotation.

Dans «Le paquet a été donné au Général.»
On annote uniquement «Général».

Dans «Il a voyagé en décembre et est allé au Mali.»
On annote «en décembre» et «au Mali».

Dans «Il a été inculpé de complicité d'enlèvement, de séquestration, de tortures».
On annote séparément «enlèvement», «séquestration» et «tortures».

Dans «La présence d’un mercenaire [...]».
On annote «un mercenaire» (le «d’» est une préposition et donc non inclus).

Dans «[...] fait partie des mercenaires …»
On annote juste «mercenaires» car «des» est une préposition (de+les).

Dans «Les informations selon lesquels des mercenaires...»
On annote en prenant l'article «des mercenaires».

Veuillez vous référer aux définitions détaillées de chaque type d’entité fournies entre les balises [definitions] ci-dessous.
Supposez que ces définitions ont été rédigées par un expert et suivez-les scrupuleusement.

[definitions]
ORGANIZATION: Organisations et personnes morales
Définition: Le label ORGANIZATION annote toutes les structures organisées qui ont une reconnaissance juridique, c'est-à-dire qui sont des personnes morales, sans inclure les organisations militaires. Ces dernières sont annotées en MILITARY_UNIT.
De manière plus détaillée, cela comprend entre autres:
- Les État, gouvernements, établissements publics, organisations internationales
- Toutes les organisations judiciaires, diplomatiques, scientifiques, d'éducation, culturelles, bancaires, sportives, de santé
- Les établissements privés comme les entreprises
Les organisations peuvent être désignées explicitement («l'OTAN», Le ministère de la Défense) ou implicitement par des adjectifs relationnels («allemand», «onusien») et des figures de style de substitution comme des périphrases ou métonymies. Il faut les annoter dans tous les cas.
Tous les groupes d'organisations sont aussi annotés, même s'ils ne sont pas des organisations en eux-mêmes («les pays d'accueil», «les plus hautes instances du pays»). Si le groupe est désigné par sa composition, on l'annote et ainsi que ses membres individuellement («américano-israélien» est annoté en entier, puis «américano» et «israélien» séparément).

GROUP: Groupes d'individus
Définition: Le label GROUP annote tous les groupes d'individus, organisés ou pas, qui ne relèvent pas de la définition d'ORGANIZATION ou de MILITARY_UNIT ou de FUNCTION.
Pour donner quelques exemples, cela recoupe les bandes organisées, la piraterie, la mafia, les pirates informatiques, les trafiquants, les manifestants, des migrants, une population, une tribu, des terroristes, une secte, une religion, une ethnie.
Un sous-ensemble d'individus d'une organisation, qui ne représente pas une organisation en soit, est considéré comme GROUP. Ainsi «des chinois» est annoté comme un GROUP contrairement à «les chinois» qui est annoté comme une ORGANIZATION.

EVENT: Evènements
Définition: Le label EVENT annote deux types d’événements: les événements historiques («La seconde Guerre Mondiale», «les guerres napoléoniennes») et les événements au sein du texte, qui sont indiqués par des amorces d’événements. Ces deux types d’événement sont définis comme suit :
 - Une amorce d’événement est, dans une phrase décrivant un événement, le mot ou groupe clé qui exprime le plus clairement et synthétiquement l’événement sujet, qu'il se produise, doit arriver, ne s'est pas réalisé ou est seulement supposé. Dans ce cas, on annote le groupe nominal minimal en EVENT c.-à-d. qu'on inclut l’article et l'adjectif seulement.
 - Un événement recoupe l'ensemble des faits qui ont une importance. On considère comme tel les faits qui ont une conséquence, sont un point de changement d'état. L'existence ou non de cet événement a une influence sur son contexte de production. De plus, on considère aussi les sentiments ou expressions d'une pensée ou état d'esprit. Ainsi, «un entretien», «servir les intérêts de» ainsi que «déclarer», «inquiéter» sont des événements.
On veut ainsi pouvoir identifier entre autres les événements de vie, de mouvement, de transaction, de commerce, de conflit, de contact entre deux personnes ou entités, de justice.
Les verbes de parole sont à annoter systématiquement en EVENT, que le sujet soit une personne («rapporte le témoin») ou tout autre entité («l'agence de presse confirme», «le gouvernement estime que», etc...
À l'exception des autres types d'entités, EVENT peut aussi servir à annoter des verbes dans le cas d'une amorce d’événement. Dans ce cas, on annote la structure minimale qui indique l’événement, c'est-à-dire uniquement le verbe, y compris au participe passé ou présent («attaqué»). Dans le cas de verbe pronominal, on ne prend pas le pronom personnel (dans «se rémunérer», on annote seulement «rémunérer»). Pour un verbe support, on annote aussi son complément nominal («proféré des menaces»). Dans le cas où une date pourrait être un événement, on peut faire le test linguistique d'insérer l'expression «l’événement qui s'est produit le» avant la date. Si la nouvelle phrase est une paraphrase de la précédente, alors c'est un événement («le 11 septembre» peut donc être annoté en EVENT selon le contexte). Dans ce cas,on ne fait pas de double annotation avec TIME.

RESOURCE: Ressources
Définition: Le label RESOURCE annote les moyens et produits dont une organisation peut disposer.
Cette catégorie, à distinguer de l'équipement, regroupe:
 - Les ressources naturelles (eau, gaz, terre, sable, pierre, métal)
 - Les produits qui résultent d’une activité industrielle (carburant, électricité, médicaments) ou agriculturale (riz, bétail, vivres)
 - Les objets numériques, tels que les services (internet, réseau téléphonique), les logiciels, les sites Web, les protocoles de communication, les réseaux sociaux, les vulnérabilités informatiques et les programmes de développement («programmes nucléaires», «programme d'armement»)
 - Les ressources monétaires
 - Les documents comme les documents d'identité, notes, journaux, déclarations écrites, documents officiels, etc., mais aussi tous les documents tels que les images, sons et vidéos.

TIME: Dates et durées
Définition: Le label TIME annote toutes les dates absolues, relatives, les périodes, etc. On considère aussi toutes les marques de fréquence («souvent», «parfois», «régulièrement») et les connecteurs logiques («d'abord», «premièrement», «puis», «enfin», «ensuite»). On annote également les prépositions s'il y en a.
On n'annote que la mention la plus précise, c'est-à-dire qu'on ne considère pas d'imbrication. Ainsi, pour la phrase «de janvier à juillet 2015», on n'annote pas «2015», puis «juillet 2015», puis «janvier 2015», etc. mais uniquement «de janvier à juillet 2015» en une seule annotation TIME. Identiquement, pour les dates abrégées («1990/91», «1978, 79, 80»), on prend l'ensemble dans une seule annotation.
Les entités de type EVENT n'ont pas besoin d'être double annotées en TIME.

MILITARY_UNIT: Unités militaires
Définition: Le label MILITARY_UNIT annote toutes les organisations qui relèvent du militaire.
Cela inclut les armées et les composantes d'armée régulières, ainsi que les désignations «vagues» d'armées («les forces russes»).
Cela comprend par exemple : «122e bataillon d'infanterie russe», «la PROVENCE», «la BA110», «la septième unité d'infanterie», «le commandement américain», «les forces de sécurité afghanes», «la coalition», «les troupes de la coalition», «une marine argentine», «les armées opposées».
Les bâtiments de la Marine sont également concernés, tels que les frégates, porte-hélicoptères et porte-avions, etc. Selon le contexte, ces derniers peuvent aussi être annotés comme EQUIPMENT ou SITE, mais ne peuvent pas avoir plusieurs labels en même temps.
Les armées dites irrégulières, c'est-à-dire qui ne sont pas affiliées à Un État ou un pouvoir légalement constitué («les paramilitaires russes»), sont annotées en GROUP. De même, les détachements incomplets sont annotés comme GROUP («des marsouins français»).

UNKNOWN: Personnes inconnues 
Définition: Le label UNKNOWN annote une personne non nommée (du moins à cette occurrence) qui ne peut être annotée ni comme PERSON ou ni comme FUNCTION. Cela inclut:
 - Les titres de civilité qui ne sont pas suivis pas Un nom propre («le monsieur»),
 - Les formulations qui ne permettent pas de comprendre l'identité précise de la personne mentionnée («le terroriste», «Un témoin», «Un cadavre»),
 - Les mentions de relations («le fils de», «le père de»).
Une personne identifiée par une fonction (un journaliste, un député, un juge d'instruction...) est annotée FUNCTION et non UNKNOWN. Mais pour une occurrence spécifique, le label UNKNOWN peut être utilisée même si la personne à laquelle il est fait référence est annotée PERSON ou FUNCTION avant ou après dans le texte.

LOCATION: Localisations
Définition: Le label LOCATION annote les noms de lieux, qu'ils soient géographiques ou administratifs (ville, pays, département, région, continent, etc.). On prend aussi en compte les adresses et les coordonnées GPS, peu importe leur système de notation: latitude/longitude, le système standard de l'OTAN (MGRS), WGS84, etc.
Pour conserver Un maximum de précision sur la localisation, il faut aussi prendre en compte les locutions prépositives («à travers», «au centre de») dans l’annotation, que la localisation soit citée explicitement après ou non («en direction de la ville», «au nord du département»).

SITE: Sites
Définition: Le label SITE annote les lieux occupés dans un but précis ou pour un intérêt ponctuel dans un événement, une construction ou un lieu qui fait l’objet d’un aménagement.
On considère comme site les lieux importants pour une activité industrielle, économique ou militaire («pont», «centrale électrique», «centre commercial»).
L'occupation peut être permanente («base militaire»), éphémère («ligne de front») ou en transit.
Les sites sont des lieux à l'échelle d'un bâtiment ou d'une infrastructure. Ils ne désignent pas une position, ou une unité plus petite («à l’intérieur du véhicule» n'est pas annoté comme SITE ou ni comme LOCATION).

FUNCTION: Fonctions
Définition: Le label FUNCTION annote les fonctions et les titres de personnes, ainsi que les grades militaires et les personnes dénommées par leur profession. Les civilités (monsieur, madame...) ne sont pas des fonctions. Il ne faudrait pas inclure le nom de la personne s'il est précisé avant ou après sa fonction (voir exemple 3); qui sera annoté en PERSON.
On considère comme fonction toute mention d'emploi, d'occupation, de qualification qui pourrait figurer sur une carte de visite.
Un groupe de personnes dénommés par leur fonction est également annoté en FUNCTION.

PERSON: Personnes nommées
Définition: Le label PERSON annote les noms propres de personnes ou d'avatars.
Les titres de civilité (Monsieur, Madame, etc.) sont à inclure dans le label, tout comme les initiales seules («JFK» pour John Fitzgerald Kennedy).
Dans les cas d'utilisation de noms propres pour désigner quelque chose de différent qu'une personne, on annote le nom si et seulement si la personne est impliquée directement dans l’objet. Ainsi, on annote les noms propres dans «l’administration Trump» et «le gouvernement Blair», mais pas dans «le Charles de Gaulle» qui désigne un navire ou dans le cas d’un nom de rue.

EQUIPMENT: Equipements
Définition: Le label EQUIPMENT annote l'ensemble du matériel pouvant appartenir à une organisation ou une personne.
Ces équipements peuvent être des objets, des systèmes techniques (matériels) ou de télécommunication, des véhicules, etc.

ID: Identifiants
Définition: Le label ID annote l'ensemble des informations qui interviennent dans le cadre d'un système informatique et/ou qui représentent une personne, permettent de contacter une personne par des moyens informatiques ou technologiques.
On prend ainsi en compte les adresses IP, de site web, les mails, numéros de téléphones, usernames, login, mots de passe, identifiants sur un réseau social, immatriculations, matricules, etc. On annote ici uniquement le contenu de l'ID.
[/definitions]

Veuillez trouver des exemples de texte d'entrée et le résultat attendu fournis entre les balises [exemples] ci-dessous.

[exemples]
Paragraphe:
La guerre au milieu des populations présente ce point commun avec la Bourse que son évolution dépend de l’action de quelques grands acteurs politiques mais surtout des anticipations de très nombreux « petits porteurs ».
Résultat:
ORGANIZATION:quelques grands acteurs politiques|la Bourse
GROUP:très nombreux « petits porteurs »|populations
EVENT:des anticipations|son évolution|La guerre

Paragraphe:
La population civile est peut-être le centre de gravité de ce type de conflit mais c’est un ensemble vivant fait d’une juxtaposition de micro-stratégies individuelles, familiales, claniques, etc. aux objectifs divers, la survie en premier lieu.
Résultat:
TIME:en premier lieu
GROUP:La population civile
EVENT:la survie|conflit

Paragraphe:
Ces civils interviennent donc de multiples façons dans la guerre depuis la simple fourniture de renseignement jusqu’à l’enrôlement dans une des armées opposées, en passant par le coup de feu occasionnel.
Résultat:
TIME:occasionnel
RESOURCE:renseignement
MILITARY_UNIT:une des armées opposées|armées opposées
GROUP:Ces civils
EVENT:le coup de feu occasionnel|la simple fourniture|l’enrôlement|la guerre

Paragraphe:
Ces milliers d’actes isolés sont parfois forcés mais le plus souvent volontaires, par intérêt ou en réaction, mais aussi par anticipation surtout lorsqu’on « sent » que l’on entre dans la phase finale de la guerre.
Résultat:
TIME:dans la phase finale de la guerre|le plus souvent|parfois
EVENT:Ces milliers d’actes isolés|anticipation|la guerre|réaction|intérêt|sent

Paragraphe:
Dans cette phase, les grands acteurs politiques armés sont plutôt incités à prendre moins de risques afin de rester sur un bilan acceptable pour la force sur le départ ou de préparer le combat suivant.
Résultat:
TIME:Dans cette phase|sur le départ|suivant
ORGANIZATION:les grands acteurs politiques armés
MILITARY_UNIT:la force
EVENT:prendre moins de risques|le combat suivant|le départ

Paragraphe:
De fait, il est préférable pour les Taliban de prendre des risques plutôt face à l’armée nationale afghane que face à des Américains sur le départ.
Résultat:
TIME:sur le départ
ORGANIZATION:les Taliban|afghane
MILITARY_UNIT:l’armée nationale afghane|des Américains
EVENT:prendre des risques|le départ

Paragraphe:
En revanche, beaucoup de familles, de clans ou de groupes divers doivent se positionner rapidement pour la suite des évènements.
Résultat:
TIME:rapidement
GROUP:groupes divers|familles|clans
EVENT:la suite des évènements|positionner

Paragraphe:
Il n’est ainsi pas rare pour une famille afghane d’avoir un fils dans l’armée nationale mais aussi dans le groupe rebelle dominant dans la région.
Résultat:
UNKNOWN:un fils
ORGANIZATION:afghane
MILITARY_UNIT:l’armée nationale
LOCATION:dans la région
GROUP:une famille afghane|le groupe rebelle 

Paragraphe:
Il peut être bon aussi de montrer sa vaillance contre les forces étrangères et la rétractation de ces dernières sur leurs bases, outre qu’elles confirment les anticipations, modifient simplement les modes d’action.
Résultat:
SITE:sur leurs bases
MILITARY_UNIT:les forces étrangères
EVENT:les anticipations|la rétractation|confirment|modifient|montrer

Paragraphe:
Au lieu d’accrocher les troupes de la coalition sur le terrain, il suffira de surveiller les axes logistiques, de lancer des projectiles sur les bases ou, si la motivation est importante, de profiter du recrutement massif des forces de sécurité afghanes pour s’infiltrer et frapper.
Résultat:
SITE:les axes logistiques|sur le terrain|sur les bases
ORGANIZATION:la coalition|afghanes
MILITARY_UNIT:les troupes de la coalition|forces de sécurité afghanes
EVENT:recrutement massif|la motivation|surveiller|accrocher|infiltrer|frapper|lancer
EQUIPMENT:des projectiles

Paragraphe:
Comme l’indiquait un journaliste français, l’attaque d’Abdul Mansour le 20 janvier dernier sur la base Gwan est sans doute le résultat non pas des Taliban ou du HiG, qui n’ont pas revendiqué l’attaque, mais de la pression de sa famille.
Résultat:
TIME:le 20 janvier dernier
SITE:sur la base Gwan
PERSON:Abdul Mansour
ORGANIZATION:français|Taliban|HiG
GROUP:sa famille
FUNCTION:un journaliste français
EVENT:la pression|revendiqué|indiquait|l’attaque|l’attaque

Paragraphe:
Les gages des « amateurs » locaux tendent ainsi à se substituer aux offensives des organisations et grands groupes, en général plus efficaces et meurtrières.
Résultat:
ORGANIZATION:grands groupes|organisations
GROUP:« amateurs » locaux
EVENT:substituer|offensives

Paragraphe:
Les pertes de la coalition en Afghanistan (mais pas celles de l’armée nationale afghane) peuvent ainsi se réduire mais pas autant qu’espéré et sans que le nombre d’incidents diminue par ailleurs.
Résultat:
ORGANIZATION:afghane
MILITARY_UNIT:l’armée nationale afghane|la coalition
LOCATION:en Afghanistan
EVENT:Les pertes|incidents|réduire|diminue

Paragraphe:
Il y a 18 soldats français tués de janvier à juillet 2011 inclus, période d’opérations actives, mais encore 11 d’août à janvier 2012, période de rétractation.
Résultat:
TIME:de janvier à juillet 2011 inclus|période d’opérations actives|période de rétractation|d’août à janvier 2012|encore
ORGANIZATION:français
GROUP:18 soldats français|11
EVENT:opérations actives|rétractation|tués

Paragraphe:
Encore ne s’agit-il là que des pertes visibles.
Résultat:
EVENT:des pertes visibles

Paragraphe:
La rétractation sur les bases et la fin des périodes offensives a un effet déprimant, tant le fait de subir est plus stressant que l’action offensive et active.
Résultat:
TIME:la fin des périodes offensives
SITE:sur les bases
EVENT:l’action offensive et active|La rétractation|offensives|déprimant|stressant|subir

Paragraphe:
Les pertes psychologiques britanniques en Irak sont devenues aussi élevées que pendant la Seconde Guerre mondiale à partir de la fin de 2005 lorsque le gouvernement Blair a réduit les opérations offensives pour des raisons électorales.
Résultat:
TIME:pendant la Seconde Guerre mondiale|à partir de la fin de 2005
PERSON:Blair
ORGANIZATION:le gouvernement Blair|britanniques
LOCATION:en Irak
EVENT:Les pertes psychologiques britanniques|la Seconde Guerre mondiale|les opérations offensives|électorales|élevées|réduit

Paragraphe:
A une toute autre échelle, l’armée américaine au Vietnam s’est effondrée moralement lorsqu’elle ne bougeait plus de ses bases après l’offensive du Têt en 1968.
Résultat:
TIME:après l’offensive du Têt en 1968
SITE:de ses bases
ORGANIZATION:américaine
MILITARY_UNIT:l’armée américaine
LOCATION:au Vietnam
EVENT:l’offensive du Têt|effondrée

Paragraphe:
Cette politique de retrait intérieur comme préalable au retrait du pays, n’est d’ailleurs pas un gage de réussite si elle ne se fonde pas sur une amélioration réelle et non racontée de la situation locale.
Résultat:
TIME:préalable au retrait du pays
LOCATION:pays
EVENT:une amélioration réelle et non racontée|retrait intérieur|réussite|retrait

Paragraphe:
Au printemps 2004, quelques jours après la capture de Saddam Hussein, le général Odierno, alors commandant de la 4e division d’infanterie déclarait que la rébellion était à genoux et que la situation serait complètement normalisée six mois plus tard.
Résultat:
TIME:quelques jours après la capture de Saddam Hussein|six mois plus tard|Au printemps 2004
PERSON:Saddam Hussein|Odierno
MILITARY_UNIT:la 4e division d’infanterie
GROUP:la rébellion
FUNCTION:commandant de la 4e division d’infanterie|le général
EVENT:la capture|normalisée|déclarait

Paragraphe:
Trois mois plus tard, les Américains devaient faire face simultanément à la résistance de Falloujah, à la révolte mahdiste et aux révélations d’Abou Ghraïb.
Résultat:
TIME:Trois mois plus tard|simultanément
ORGANIZATION:les Américains|mahdiste
LOCATION:Abou Ghraïb|Falloujah
EVENT:la révolte mahdiste|la résistance|révélations|faire face

Paragraphe:
A la fin de 2005, après la reprise des villes tenues par les rebelles et la réussite des élections, les Américains se repliaient dans de grandes bases.
Résultat:
TIME:après la reprise des villes tenues par les rebelles et la réussite des élections|A la fin de 2005
SITE:villes tenues par les rebelles|dans de grandes bases
ORGANIZATION:les Américains
GROUP:les rebelles
EVENT:la réussite|la reprise|repliaient|élections

Paragraphe:
Quelques semaines plus tard, l’Irak basculait dans la guerre civile.
Résultat:
TIME:Quelques semaines plus tard
LOCATION:l’Irak
EVENT:la guerre civile

Paragraphe:
L’exécutif américain a eu au moins le courage de changer de stratégie, changement lui-même rendu possible par l’acceptation d’une pensée militaire critique par le commandement américain.
1/29/2012
Résultat:
TIME:1/29/2012
ORGANIZATION:L’exécutif américain|américain|américain
MILITARY_UNIT:le commandement américain
EVENT:une pensée militaire critique|l’acceptation|changer

Paragraphe:
En Iran, exécution de quatre personnes accusées de coopération avec les services de renseignement israéliens...
Résultat:
ORGANIZATION:les services de renseignement israéliens|israéliens
LOCATION:En Iran
GROUP:quatre personnes
EVENT:coopération|exécution|accusées

Paragraphe:
Quatre personnes accusées d’avoir coopéré avec l’agence de renseignement israélienne Mossad ont été exécutées dimanche en Iran, a rapporté l’agence de presse iranienne Fars.
Résultat:
TIME:dimanche
ORGANIZATION:l’agence de renseignement israélienne Mossad|l’agence de presse iranienne Fars|israélienne|iranienne
LOCATION:en Iran
GROUP:Quatre personnes
EVENT:exécutées|accusées|rapporté|coopéré

Paragraphe:
L’Iran accuse régulièrement Israël de mener des opérations secrètes sur son sol. Téhéran estime que les services de renseignement israéliens et occidentaux sont à l’origine de la vague de contestation qui secoue le pays depuis plus de trois mois.
Résultat:
TIME:depuis plus de trois mois|régulièrement
SITE:sur son sol
ORGANIZATION:les services de renseignement israéliens|occidentaux|israéliens|Téhéran|L’Iran|Israël
LOCATION:le pays
EVENT:la vague de contestation|des opérations secrètes|accuse|estime
DISC_ORGANIZATION:les services de renseignement israéliens et occidentaux

Paragraphe:
Mercredi, l’agence de presse Mehr a déclaré que les quatre hommes avaient été condamnés à mort pour avoir coopéré avec les services de renseignement du régime sioniste et pour enlèvement.
Résultat:
TIME:Mercredi
ORGANIZATION:les services de renseignement du régime sioniste|l’agence de presse Mehr|régime sioniste
GROUP:les quatre hommes
EVENT:condamnés à mort|enlèvement|déclaré|coopéré

Paragraphe:
En Iran, les pompes à essence paralysées suite à une cyberattaque...
Résultat:
RESOURCE:essence
LOCATION:En Iran
EVENT:une cyberattaque|paralysées
EQUIPMENT:les pompes à essence

Paragraphe:
La panne générale de distribution de carburant survenue mardi en Iran est due à une cyberattaque a affirmé la plus haute instance sécuritaire du pays.
Résultat:
TIME:mardi
RESOURCE:carburant
ORGANIZATION:la plus haute instance sécuritaire du pays|pays
LOCATION:en Iran
EVENT:La panne générale|une cyberattaque|affirmé

Paragraphe:
« Le Conseil suprême de la sécurité nationale a confirmé qu'il s'agissait d'une cyberattaque contre le système informatique de distribution du carburant » a indiqué la télévision d’État.
Résultat:
RESOURCE:carburant
ORGANIZATION:Le Conseil suprême de la sécurité nationale|la télévision d’État
EVENT:une cyberattaque|confirmé|indiqué
EQUIPMENT:le système informatique de distribution du carburant

Paragraphe:
La panne d'un système informatique géré par le gouvernement régissant l'approvisionnement des stations-services à travers le pays a engendré mardi une pénurie de carburant à l'échelle nationale.
Résultat:
TIME:mardi
SITE:stations-services
RESOURCE:carburant
ORGANIZATION:le gouvernement
LOCATION:à l'échelle nationale|à travers le pays
EVENT:l'approvisionnement|une pénurie|La panne 
EQUIPMENT:un système informatique

Paragraphe:
Des images de longues files d'attente de véhicules à l'entrée des stations-services à Téhéran ont été diffusées par la télévision d’État iranienne.
Résultat:
SITE:à l'entrée des stations-services
RESOURCE:Des images
ORGANIZATION: la télévision d’État iranienne|iranienne
LOCATION:à Téhéran
EVENT:longues files d'attente|diffusées
EQUIPMENT:véhicules

Paragraphe:
Les responsables du ministère du Pétrole doivent organiser une réunion d'urgence pour résoudre le problème technique, qui pour l'heure n'a pas été détaillé.
Résultat:
TIME:pour l'heure
ORGANIZATION:ministère du Pétrole
GROUP:Les responsables du ministère du Pétrole
EVENT:une réunion d'urgence|résoudre

Paragraphe:
Selon l'agence de presse semi-officielle ISNA, les utilisateurs de carburant auraient reçu un message indiquant « cyberattaque 64411 », un numéro d'urgence lié au bureau du guide suprême iranien, l'ayatollah Ali Khamenei.
Résultat:
RESOURCE:un numéro d'urgence|carburant
PERSON:Ali Khamenei
ORGANIZATION:l'agence de presse semi-officielle ISNA|bureau du guide suprême iranien|iranien
ID:64411
GROUP:les utilisateurs de carburant
FUNCTION:guide suprême iranien|l'ayatollah
EVENT:cyberattaque|reçu

Paragraphe:
Aucun groupe n'a revendiqué la responsabilité de la panne.
Résultat:
EVENT:revendiqué|la panne

Paragraphe:
Cependant, le numéro 64411 rappelle la cyberattaque commise contre le système ferroviaire iranien au mois de juillet, des pirates avaient alors modifié l'affichage dans les gares en demandant aux passagers de composer le 64411.
Résultat:
TIME:au mois de juillet
SITE:dans les gares
ORGANIZATION:iranien
ID:64411|64411
GROUP:des pirates|passagers
EVENT:la cyberattaque|modifié
EQUIPMENT:le système ferroviaire iranien|l'affichage

Paragraphe:
L'Iran a déjà fait l'objet de plusieurs cyberattaques, dont une au mois d'août sur la prison d'Evine à Téhéran, lors de laquelle des hackers avaient obtenu des vidéos internes montrant des violences sur des détenus. À la fin des années 2000, l'Iran avait par ailleurs déconnecté une grande partie de son infrastructure gouvernementale des services internet après l'introduction du virus informatique Stuxnet - considéré comme une conception conjointe américano-israélienne - qui avait perturbé le programme nucléaire iranien, ciblant les centrifugeuses de la centrale de Natanz.
Résultat:
TIME:après l'introduction du virus informatique Stuxnet|À la fin des années 2000|au mois d'août
SITE:sur la prison d'Evine|la centrale de Natanz
RESOURCE:le programme nucléaire iranien,|virus informatique Stuxnet|des vidéos internes|services internet
ORGANIZATION:américano-israélienne|israélienne|américano|iranien|L'Iran|l'Iran
LOCATION:à Téhéran|Natanz
ID:Stuxnet
GROUP:des hackers|des détenus
EVENT:plusieurs cyberattaques|l'introduction|des violences|déconnecté|perturbé|obtenu
EQUIPMENT:les centrifugeuses de la centrale de Natanz|son infrastructure gouvernementale

Paragraphe:
Exercices militaires tactiques de l’armée russe en Biélorussie...
Résultat:
ORGANIZATION:russe
MILITARY_UNIT:l’armée russe
LOCATION:en Biélorussie
EVENT:Exercices militaires tactiques

Paragraphe:
Les troupes russes mènent des exercices tactiques en Biélorussie dans un paysage hivernal, annonce ce jeudi 8 décembre le ministère russe de la Défense dans un communiqué.
Résultat:
TIME:ce jeudi 8 décembre|hivernal
RESOURCE:un communiqué
ORGANIZATION:le ministère russe de la Défense|russes|russe
MILITARY_UNIT:Les troupes russes
LOCATION:en Biélorussie
EVENT:des exercices tactiques|annonce

Paragraphe:
« Les militaires de la région militaire ouest poursuivent leur entraînement intensif au combat dans les champs de tir des forces armées de la République de Biélorussie.
Résultat:
SITE:dans les champs de tir des forces armées de la République de Biélorussie
ORGANIZATION:la République de Biélorussie|la région militaire ouest
MILITARY_UNIT:forces armées de la République de Biélorussie|Les militaires de la région militaire ouest
EVENT:leur entraînement intensif

Paragraphe:
L’entraînement au combat a lieu de jour comme de nuit » indique-t-il.
Résultat:
TIME:de jour comme de nuit
EVENT:L’entraînement|indique

Paragraphe:
Les militaires tirent avec tous les types d'armes légères, ainsi qu'avec des mortiers.
Résultat:
GROUP:Les militaires
EVENT:tirent
EQUIPMENT:tous les types d'armes légères|des mortiers

Paragraphe:
Ils perfectionnent leurs compétences dans la conduite de véhicules de combat, réussissent des parcours d'obstacles psychologiques, étudient la médecine tactique et d'autres disciplines.
Résultat:
EVENT:perfectionnent|réussissent|étudient
EQUIPMENT:véhicules de combat

Paragraphe:
Des clips vidéo publiés par le ministère montrent des soldats russes en tenue de neige s'entraînant près de chars dans un paysage hivernal, tirant avec des armes, notamment de l'artillerie.
Résultat:
TIME:hivernal
RESOURCE:Des clips vidéo
ORGANIZATION:le ministère|russes
GROUP:des soldats russes
EVENT:s'entraînant|publiés|tirant
EQUIPMENT:tenue de neige|l'artillerie|des armes|chars

Paragraphe:
La Russie a envoyé un groupe de ses soldats en Biélorussie en octobre pour participer à une nouvelle force conjointe avec les troupes du pays hôte pour renforcer la protection et la défense de la frontière avec l'Ukraine.
Résultat:
TIME:en octobre
SITE:la frontière avec l'Ukraine
ORGANIZATION:La Russie|pays hôte
MILITARY_UNIT:les troupes du pays hôte|une nouvelle force
LOCATION:en Biélorussie| l'Ukraine
GROUP:un groupe de ses soldats
EVENT:la protection|participer|la défense|renforcer|envoyé

Paragraphe:
L'éventuel déploiement de paramilitaires russes au Mali inquiète Washington...
Résultat:
ORGANIZATION:Washington|russes
LOCATION:au Mali
GROUP:paramilitaires russes
EVENT:L'éventuel déploiement|inquiète

Paragraphe:
Les États-Unis s'inquiètent d'un éventuel déploiement de paramilitaires russes au Mali.
Résultat:
ORGANIZATION:Les États-Unis|russes
LOCATION:au Mali
GROUP:paramilitaires russes
EVENT:un éventuel déploiement|inquiètent

Paragraphe:
Dans un communiqué, Linda Thomas-Greenfield, la représentante américaine permanente aux Nations unies, a fait part de ses inquiétudes.
Résultat:
RESOURCE:un communiqué
PERSON:Linda Thomas-Greenfield
ORGANIZATION:Nations unies|américaine
FUNCTION:la représentante américaine permanente aux Nations unies
EVENT:ses inquiétudes|fait part

Paragraphe:
« J'ai exprimé notre sérieuse inquiétude au sujet des informations selon lesquelles des mercenaires russes pourraient être déployés au Mali » a-t-elle déclaré à l'issue d'un entretien à Niamey avec le président nigérien Mohamed Bazoum.
Résultat:
TIME:à l'issue d'un entretien
RESOURCE:informations
PERSON:Mohamed Bazoum
ORGANIZATION:nigérien|russes
LOCATION:à Niamey|au Mali
GROUP:des mercenaires russes
FUNCTION:le président nigérien
EVENT:notre sérieuse inquiétude|un entretien|déployés|exprimé|déclaré

Paragraphe:
Madame Linda Thomas-Greenfield fait partie d'une délégation du Conseil de sécurité de l'ONU qui s'est rendue le week-end dernier à Bamako afin de faire pression pour le rétablissement du pouvoir civil au Mali.
Résultat:
TIME:le week-end dernier
PERSON:Madame Linda Thomas-Greenfield
ORGANIZATION:une délégation du Conseil de sécurité de l'ONU|Conseil de sécurité de l'ONU|l'ONU
LOCATION:à Bamako|au Mali
EVENT:le rétablissement du pouvoir civil|faire pression|fait partie|rendue

Paragraphe:
La délégation s'est ensuite rendue au Niger.
Résultat:
TIME:ensuite
ORGANIZATION:La délégation
LOCATION:au Niger
EVENT:rendue

Paragraphe:
La représentante des États-Unis à l'ONU a estimé que les paramilitaires russes sont pointés du doigt dans des abus sur des civils et que leur présence va aggraver probablement la situation sécuritaire actuelle.
Résultat:
TIME:actuelle
ORGANIZATION:États-Unis|russes|l'ONU
GROUP:les paramilitaires russes|des civils
FUNCTION:La représentante des États-Unis à l'ONU
EVENT:pointés du doigt|leur présence|des abus|aggraver|estimé

Paragraphe:
La France et l'Allemagne ont prévenu qu'un accord entre Bamako et Wagner remettrait en cause leur présence militaire au Mali.
Résultat:
ORGANIZATION:l'Allemagne|La France|Bamako|Wagner
LOCATION:au Mali
EVENT:leur présence militaire|un accord|prévenu

Paragraphe:
Paris accuse le groupe Wagner de se rémunérer sur les ressources des pays d'accueil comme le Centrafrique et la Libye, et de servir les intérêts du Kremlin.
Résultat:
RESOURCE:les ressources des pays d'accueil
ORGANIZATION:le groupe Wagner|le Centrafrique|pays d'accueil|la Libye|Kremlin|Paris
EVENT:servir les intérêts|rémunérer|accuse

Paragraphe:
Ce que dément catégoriquement le président russe Vladimir Poutine.
Résultat:
PERSON:Vladimir Poutine
ORGANIZATION:russe
FUNCTION:le président russe
EVENT:dément

Paragraphe:
Il s'agit d’une cyberattaque contre le système de distribution du carburant.
Résultat:
RESOURCE:carburant
EVENT:cyberattaque
EQUIPMENT:le système de distribution du carburant

Paragraphe:
L'Iran avait par ailleurs déconnecté une grande partie de son infrastructure gouvernementale des services internet [...].
Résultat:
RESOURCE:services internet
ORGANIZATION:L'Iran
EVENT:déconnecté
EQUIPMENT:son infrastructure gouvernementale

Paragraphe:
Les habitants attendent avec impatience la levée de l'embargo dans les jours suivants.
Résultat:
TIME:dans les jours suivants
GROUP:Les habitants
EVENT:la levée de l'embargo|impatience|l'embargo

Paragraphe:
En Iran, exécution de quatre personnes accusées de coopération avec les services de renseignement israéliens.
Résultat:
ORGANIZATION:les services de renseignement israéliens|israéliens
LOCATION:En Iran
GROUP:quatre personnes
EVENT:coopération|exécution|accusées

Paragraphe:
Dans un communiqué, Linda Thomas-Greenfield fait part de ses inquiétudes.
Résultat:
RESOURCE:un communiqué
PERSON:Linda Thomas-Greenfield
EVENT:inquiétudes|fait part

Paragraphe:
Les paramilitaires russes ont été déployés au Mali.
Résultat:
ORGANIZATION:russes
LOCATION:au Mali
GROUP:paramilitaires russes
EVENT:déployés

Paragraphe:
La panne générale du système de distribution de carburant ...
Résultat:
RESOURCE:carburant
EVENT:La panne générale
EQUIPMENT:système de distribution de carburant

Paragraphe:
L'officier de police fait état de quatre tués et cinq blessés parmi les joueurs.
Résultat:
GROUP:cinq blessés|quatre tués|les joueurs
FUNCTION:L'officier de police
EVENT:fait état|blessés|tués

Paragraphe:
Les membres de l'ONU ont voté mardi matin.
Résultat:
TIME:mardi matin
ORGANIZATION:Les membres de l'ONU|l'ONU
EVENT:voté

Paragraphe:
Les paramilitaires russes sont pointés du doigt dans des abus sur des civils.
Résultat:
ORGANIZATION:russes
GROUP:Les paramilitaires russes|des civils
EVENT:pointés du doigt|des abus

Paragraphe:
Un ancien chef des services de renseignement a été arrêté hier dans l'enquête sur la disparition d’un journaliste en 2016.
Résultat:
TIME:en 2016|hier
ORGANIZATION:services de renseignement
FUNCTION:Un ancien chef des services de renseignement|un journaliste
EVENT:l'enquête|arrêté

Paragraphe:
L'ambassadeur américain à Séoul a pris la parole sur la situation.
Résultat:
ORGANIZATION:américain
LOCATION:à Séoul
FUNCTION:L'ambassadeur américain à Séoul
EVENT:pris la parole

Paragraphe:
L'enquête porte sur la disparition du journaliste Birama Touré.
Résultat:
PERSON:Birama Touré
FUNCTION:journaliste
EVENT:la disparition|L'enquête

Paragraphe:
L'assaillant a été arrêté, selon le porte-parole de la police.
Résultat:
UNKNOWN:L'assaillant
ORGANIZATION:la police
FUNCTION:le porte-parole de la police
EVENT:arrêté

Paragraphe:
Les généraux se sont réunis [...].
Résultat:
FUNCTION:Les généraux
EVENT:réunis

Paragraphe:
Quatre joueurs du club de football local ont été aperçus.
Résultat:
FUNCTION:Quatre joueurs du club de football local
EVENT:aperçus

Paragraphe:
Dans l'attaque, plusieurs soldats français ont été blessés [...].
Résultat:
FUNCTION:plusieurs soldats
EVENT:l'attaque|blessés

Paragraphe:
L'utilisateur @baba a proféré des menaces en ligne via Facebook.
Résultat:
UNKNOWN:L'utilisateur
RESOURCE:en ligne|Facebook
ID:@baba
EVENT:proféré des menaces

Paragraphe:
Les utilisateurs de carburant auraient reçu un message indiquant “cyberattaque 64411".
Résultat:
RESOURCE:carburant
ID:64411
GROUP:Les utilisateurs de carburant
EVENT:cyberattaque|reçu

Paragraphe:
Les troupes ont progressé à travers le pays.
Résultat:
MILITARY_UNIT:Les troupes
LOCATION:à travers le pays
EVENT:progressé

Paragraphe:
De nouveaux missiles ont été lancés depuis la Corée du Nord.
Résultat:
LOCATION:la Corée du Nord
EVENT:lancés
EQUIPMENT:De nouveaux missiles

Paragraphe:
La Corée du Nord a lancé de nouveaux missiles.
Résultat:
ORGANIZATION:La Corée du Nord
EVENT:lancé
EQUIPMENT:de nouveaux missiles

Paragraphe:
L'armée russe est en mouvement.
Résultat:
ORGANIZATION:russe
MILITARY_UNIT:L'armée russe
EVENT:mouvement

Paragraphe:
Les paramilitaires russes ont attaqué une ville.
Résultat:
ORGANIZATION:russes
LOCATION:une ville
GROUP:Les paramilitaires russes
EVENT:attaqué

Paragraphe:
L'éventuel déploiement de paramilitaires russes au Mali inquiète Washington.
Résultat:
ORGANIZATION:Washington|russes
LOCATION:au Mali
GROUP:paramilitaires russes
EVENT:L'éventuel déploiement|inquiète

Paragraphe:
La secrétaire au bureau du Conseil de Sécurité de l'ONU.
Résultat:
ORGANIZATION:bureau du Conseil de Sécurité de l'ONU|Conseil de Sécurité de l'ONU|l'ONU
FUNCTION:La secrétaire au bureau du Conseil de Sécurité de l'ONU

Paragraphe:
Les services de renseignement israélien et occidentaux.
Résultat:
ORGANIZATION:Les services de renseignement israélien et occidentaux|occidentaux|israélien

Paragraphe:
Ce que dément catégoriquement le président russe Vladimir Poutine.
Résultat:
PERSON:Vladimir Poutine
ORGANIZATION:russe
FUNCTION:le président russe
EVENT:dément

Paragraphe:
Madame Linda Thomas-Greenfield fait partie d'une délégation du Conseil de Sécurité de l'ONU.
Résultat:
PERSON:Madame Linda Thomas-Greenfield
ORGANIZATION:une délégation du Conseil de Sécurité de l'ONU|Conseil de Sécurité de l'ONU|l'ONU

Paragraphe:
L'artiste Banksy a réalisé une nouvelle œuvre à Londres.
Résultat:
PERSON:Banksy
LOCATION:à Londres
FUNCTION:artiste

Paragraphe:
L'organisation bénéficie d'un accès à internet par le biais des antennes relais qu'elle a installé dans l’ensemble de la région.
Résultat:
RESOURCE:internet
LOCATION:dans l’ensemble de la région
EVENT:installé
EQUIPMENT:antennes relais

Paragraphe:
Un virus informatique a été envoyé à plus de 200 personnes.
Résultat:
RESOURCE:Un virus informatique
GROUP:200 personnes
EVENT:envoyé

Paragraphe:
Pyongyang avait fourni des composants de missiles à longue portée.
Résultat:
RESOURCE:des composants
ORGANIZATION:Pyongyang
EVENT:fourni
EQUIPMENT:missiles à longue portée

Paragraphe:
Dans un communiqué, la représentante américaine fait part de son inquiétude.
Résultat:
RESOURCE:un communiqué
ORGANIZATION:américaine
FUNCTION:la représentante américaine
EVENT:son inquiétude|fait part

Paragraphe:
Des images de longues files d'attente de véhicules à l'entrée des stations-services.
Résultat:
SITE:stations-services
RESOURCE:Des images
EVENT:longues files d'attente
EQUIPMENT:véhicules

Paragraphe:
Après l'introduction du virus informatique Stuxnet [...] visant les centrifugeuses de la centrale de Natanz.
Résultat:
TIME:Après l'introduction du virus informatique Stuxnet
SITE:la centrale de Natanz
RESOURCE:virus informatique Stuxnet
LOCATION:Natanz
ID:Stuxnet
EVENT:l'introduction
EQUIPMENT:les centrifugeuses

Paragraphe:
À la fin des années 2000, l'Iran avait par ailleurs [...].
Résultat:
TIME:À la fin des années 2000
ORGANIZATION:l'Iran

Paragraphe:
L'embargo sur les armes à été prolongé jeudi de douze mois.
Résultat:
TIME:douze mois|jeudi
EVENT:L'embargo|prolongé
EQUIPMENT:les armes

Paragraphe:
Demain matin nous aurons des réponses, mais pour l'heure rien n'est sûr.

[..] dans la phase finale de la guerre.
Résultat:
TIME:dans la phase finale de la guerre|Demain matin|pour l'heure
EVENT:la guerre

Paragraphe:
La fin des périodes offensives [...].
Résultat:
TIME:La fin des périodes offensives
EVENT:offensives

Paragraphe:
J'ai vu le car brûler a indiqué un témoin.
Résultat:
UNKNOWN:un témoin
EVENT:brûler
EQUIPMENT:le car

Paragraphe:
Le fils de l’ancien président Ibrahim Boubacar Keita.
Résultat:
UNKNOWN:Le fils de l’ancien président Ibrahim Boubacar Keita
PERSON:Ibrahim Boubacar Keita
FUNCTION:l’ancien président

Paragraphe:
Le responsable du ministère du Pétrole doit organiser une réunion d'urgence.
Résultat:
ORGANIZATION:ministère du Pétrole
FUNCTION:Le responsable du ministère du Pétrole
EVENT:une réunion d'urgence

Paragraphe:
John Smith a été cambriolé.
Résultat:
PERSON:John Smith
EVENT:cambriolé

Paragraphe:
La victime déplore un grand préjudice.
Résultat:
UNKNOWN:La victime
EVENT:déplore
[/exemples]

Voici un exemple de format de sortie pour un paragraphe utilisant des étiquettes différentes de celles requises pour cette tâche.
Utilisez uniquement ce format de sortie mais utilisez les étiquettes fournies ci-dessus au lieu de celles définies dans l'exemple ci-dessous.
ci-dessus au lieu de celles définies dans l'exemple ci-dessous.
Le résultat doit donner une ligne pour chaque étiquette extraite, cette ligne doit commencer par l'étiquette suivie d'une liste d'entités séparées par le caractère | telles qu'elles apparaissent dans le paragraphe d'entrée et dans leur ordre d'apparition.
Ne produisez rien d'autre que des entités dans ce format de sortie.

Paragraphe : La sauce Sriracha et les oignons se marient très bien avec le sauté de hoisin, mais vous devez l'ajouter après avoir utilisé le wok et bien remué avec une cuillère en bois.
Résultat :
INGREDIENT:La sauce Sriracha|les oignons
DISH:le sauté de hoisin
EQUIPMENT:wok|cuillère en bois

Paragraphe:
{{ doc.text }}
Résultat:"""

    parameters = OpenAICompletionParameters(
        model='gpt-4-32k-0314',
        max_tokens=10000,
        temperature=0.2,
        prompt=prompt,
        function=OpenAIFunction.add_annotations,
        candidate_labels=candidate_labels
    )
    processor = OpenAICompletionProcessor()
    docs = [
        Document(
            identifier="1",
            text="Selon l'agence de presse semi-officielle ISNA, les utilisateurs de carburant auraient reçu un message indiquant « cyberattaque 64411 », un numéro d'urgence lié au bureau du guide suprême iranien, l'ayatollah Ali Khamenei.",
            metadata={"language": "fr"},
        ),
    ]
    docs = processor.process(docs, parameters)
    assert docs == HasLen(1)
    doc0 = docs[0]
    for a in doc0.annotations:
        assert a.text == doc0.text[a.start:a.end]


@pytest.fixture
def expected_en():
    return {
        "Sport": "The french team is going to win Euro 2021 football tournament",
        "Politics": "Who are you voting for in 2021?",
        "Science": "Coronavirus vaccine research are progressing",
    }


@pytest.mark.skip(reason="Not a test")
def test_function_call_cat(expected_en):
    candidate_labels = {
        'sport': 'Sport',
        'politics': 'Politics',
        'science': 'Science',
    }

    EXCL_CLAUSE = "\nThe task is exclusive, so only choose one label from what I provided and write it as a single line.\n"
    NO_EXCL_CLAUSE = "\nThe task is not exclusive, so if more than one label is possible, please just write one label per line.\n"

    excl_prompt = """You are an expert Text Classification system. Your task is to accept Text as input and provide a category for the text based on the predefined labels.
{%- set labels=[] -%}
{%- for l in parameters.candidate_labels.values() -%}
  {%- do labels.append('"' + l + '"') -%}
{%- endfor %}
Classify the text below to one of the following labels: {{ labels|join(', ') }}
The task is exclusive, so only choose one label from what I provided and write it as a single line.""" + EXCL_CLAUSE + """Text: {{doc.text}}
Result:
"""
    no_excl_prompt = """You are an expert Text Classification system. Your task is to accept Text as input and provide a category for the text based on the predefined labels.
    {%- set labels=[] -%}
    {%- for l in parameters.candidate_labels.values() -%}
      {%- do labels.append('"' + l + '"') -%}
    {%- endfor %}
    Classify the text below to one of the following labels: {{ labels|join(', ') }}
    The task is exclusive, so only choose one label from what I provided and write it as a single line.""" + NO_EXCL_CLAUSE + """Text: {{doc.text}}
    Result:
    """
    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo,
        completion_altText=None,
        prompt=excl_prompt,
        function=OpenAIFunction.add_categories,
        candidate_labels=candidate_labels
    )
    processor = OpenAICompletionProcessor()
    docs = [Document(text=t) for t in expected_en.values()]
    docs = processor.process(docs, parameters)
    for expected_label, doc in zip(expected_en.keys(), docs):
        assert doc.categories[0].label == expected_label

    parameters.prompt = no_excl_prompt
    docs = [Document(text=t) for t in expected_en.values()]
    docs = processor.process(docs, parameters)
    for expected_label, doc in zip(expected_en.keys(), docs):
        assert doc.categories[0].label == expected_label


@pytest.mark.skip(reason="Not a test")
def test_cairninfo():
    prompt = """Refais la ponctuation du texte suivant en français. Ce texte comporte plusieurs interlocuteurs. Va à la ligne à chaque fois que l'interlocuteur change : $text"""

    parameters = DeepInfraOpenAICompletionParameters(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        max_tokens=4000,
        completion_altText=None,
        prompt=prompt,
    )
    processor = DeepInfraOpenAICompletionProcessor()
    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/test_cairninfo-document-CNRRENC_013.txt.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        doc = Document(**jdoc)
        seg0 = Document(text=doc.text[doc.sentences[0].start:doc.sentences[0].end])
        segs = processor.process([seg0], parameters)
        assert segs == HasLen(1)
        sum_file = testdir / "data/test_cairninfo-document-CNRRENC_013.seg0.json"
        dl = DocumentList(__root__=segs)
        with sum_file.open("w") as fout:
            print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
    # noqa: E501


@pytest.mark.skip(reason="Not a test")
def test_resume_mixtral():
    text = """Jérusalem, ville sainte contestée
La situation ecclésiale diverse et complexe
Matthias Vogt

Jérusalem, ville sainte de trois religions, lieu de la passion, de la mort et de la résurrection de Jésus Christ, berceau du christianisme, destination de pèlerinages de millions de chrétiens du monde entier, lieu de rêves pour beaucoup qui, pour des raisons sociales ou politiques ne peuvent s’y rendre dont les chrétientés de la majorité de pays arabes et de beaucoup de pays qui se disent musulmans. Jérusalem, centre de la communauté chrétienne naissante dont témoignent les Actes des Apôtres, « Église-mère » de toutes les Églises, comme aiment à le répéter les clercs de la ville sainte, noyau de l’œcuménisme mais aussi point chaud de conflits interconfessionnels et foyer d’une communauté chrétienne multiforme. C’est sur la situation des Églises de Jérusalem et des chrétiens de la ville que nous voulons mettre l’accent dans cet article.
Situation actuelle de Jérusalem
De nos jours, Jérusalem est une ville d’environ 966 000 habitants dont la majorité sont juifs (567 000 ou 59 %) et environ 366 000 musulmans (38 %). Selon les données de l’année 2021 publiées par le Bureau israélien des statistiques, il y a à Jérusalem, Est et Ouest confondus, 12 900 chrétiens (1,3 % de la population totale), dont 9800 chrétiens arabes (ou 2,6 % de la population arabe). En 1944, les chrétiens comptent 19 % de la population (29 400 chrétiens parmi 30 600 musulmans et 97 000 juifs) ou quasiment la moitié de la population non-juive de la ville. Il faut donc constater une chute dramatique de la quote-part chrétienne. Ce qui pèse lourd chez les chrétiens de Jérusalem, c’est que cette ville considérée comme un « espace chrétien » n’existe plus, en tant que telle, depuis 1948 malgré la multitude d’églises, de lieux saints et d’institutions chrétiennes.
Pour les Juifs, Jérusalem est considérée la ville la plus conservatrice du pays. Avec son grand nombre d’écoles religieuses (yeshiva, pl. yeshivot), surtout dans le quartier juif de la vieille ville, le nombre croissant de quartiers ultra-orthodoxes à Jérusalem-Ouest et la présence de groupes nationalistes juifs à l’intérieur des murailles médiévales, l’ambiance dans la ville est de plus en plus hostile aux populations chrétienne et musulmane. Les implantations des colons nationalistes et religieux dans les quartiers chrétiens et musulmans de la vieille ville et dans les quartiers résidentiels arabes de Jérusalem-Est (surtout Sheikh Jarrah, Abu Tor et Silwan) constituent une provocation envers les habitants palestiniens et sont les lieux de multiples conflits violents entre colons, Palestiniens et forces de l’ordre israéliennes.
Pour les musulmans, Jérusalem se trouve au centre des préoccupations palestiniennes mais aussi mondiales vu l’importance des sanctuaires islamiques sur le Haram al-Sharîf. Deux mouvements islamiques extrémistes sont présents dans la ville : le Hamas (Mouvement de résistance islamique), né de la Société des Frères musulmans, et le Hizb al-tahrîr (Parti de la libération), mouvement islamique international, né en Palestine, qui vise à imposer l’application stricte de la loi islamique (sharî’a) et à établir un état islamique de type califal. Les deux mouvements se montrent peu favorables aux non-musulmans auxquels ils assignent, dans leur projet de cité, une place régie par les lois islamiques, c’est-à-dire un statut inférieur à celui des musulmans. Les manifestations des adhérents à ces deux mouvements, surtout aux alentours de la mosquée al-Aqsa, créent une ambiance peu rassurante pour les chrétiens de Jérusalem et remettent en question, de plus en plus, l’unité entre chrétiens et musulmans à cause du mouvement national palestinien.
Les Palestiniens de Jérusalem, chrétiens et musulmans, participent peu à la vie politique de la ville : dans les élections municipales les suffrages arabes sont bas, la participation à la chose publique étant considérée comme contribution à la « normalisation » d’une situation irrégulière. Ce n’est donc pas seulement à cause de la majorité absolue des habitants juifs de Jérusalem que la municipalité est dominée par la composante juive. Pour la politique israélienne, aussi bien sur le plan national que municipal, il n’y a aucun doute que Jérusalem est la « capitale éternelle et indivisible » de l’État juif telle que déclarée, en 1980, par la Knesset, le parlement israélien.
Les projets d’aménagement et de développement pris en charge par la municipalité de Jérusalem, sont considérés par la population arabe comme des tentatives plus ou moins dissimulées d’appropriation de terrains qui se trouvent encore entre les mains de propriétaires palestiniens. Des parcelles appartenant aux Églises ainsi qu’à des congrégations religieuses sont aussi menacées. Le projet d’aménagement d’un parc national sur les terrains pentus du Mont des Oliviers qui appartiennent à des Églises suscite l’inquiétude des chefs d’Églises. De même, l’acquisition par les associations de colons juifs d’immeubles, dans le quartier chrétien de la vieille ville, a suscité la critique des représentants des Églises. Même si certaines de ces transactions immobilières sont légales, les prix offerts, souvent le double du prix du marché, laissent apparaître un manque de droiture morale. La non-ingérence des autorités israéliennes compétentes trahit l’absence de volonté de protéger l’équilibre traditionnel et fragile des communautés religieuses dans la ville sainte.
La situation ecclésiale et œcuménique
Les chrétiens de Jérusalem se répartissent sur 13 communautés reconnues ; du côté orthodoxe : grecque, arménienne, syriaque, copte et éthiopienne ; du côté catholique : latine (catholique romaine), grec-melkite, arménienne, syriaque, maronite et chaldéenne ; du côté des Églises issues de la Réforme : épiscopale (anglicane) et luthérienne, sans compter différentes communautés protestantes et pentecôtistes non reconnues. Ces Églises comptent un nombre inégal de croyants de langue arabe vivant à Jérusalem : les catholiques de rite latin sont environ 5400 (55 %), les grecs orthodoxes 2300 (23 %), les melkites 860 (9 %), les arméniens orthodoxes 500 (5 %), les syriens orthodoxes 400 (4 %) et les autres 330 (3 %).
L’Église grecque-orthodoxe est dirigée par le patriarche de Jérusalem, assisté dans l’exercice de ses fonctions par 14 évêques titulaires. Ils sont tous membres de la Confrérie du Saint-Sépulcre (Confrérie des hagiotaphites) dont la mission est de préserver les propriétés de l’Église orthodoxe dans les lieux saints et de préserver le caractère hellénique du patriarcat. La communauté arabe est représentée dans la Confrérie par un seul évêque d’origine palestinienne ou jordanienne. Le fait que le clergé supérieur soit presque exclusivement grec, alors que les prêtres et les fidèles sont arabes, provoque régulièrement des tensions et des reproches de la part du laïcat selon lesquels la hiérarchie ne défend pas avec suffisamment de vigueur les intérêts de la communauté face à l’État israélien. Les activités sociales et humanitaires sont principalement menées par des associations de laïcs. Depuis les années 1990, les croyants arabes sont préoccupés par l’immigration en provenance des pays de l’ex-Union soviétique qui a entraîné une nette augmentation de communautés orthodoxes de langue non arabe. Ces fidèles vivent entièrement dans le milieu juif israélien et n’ont aucun contact avec les communautés arabes. Par leur présence, le caractère jusqu’alors presque exclusivement arabe de la communauté grecque-orthodoxe de Jérusalem et de Terre Sainte s’est affaibli. Cela ne renforce pas les prétentions des laïcs arabes d’avoir leur mot à dire dans la gestion des biens et leur demande d’arabisation du patriarcat.
L’Église romaine catholique (latine) est représentée par le patriarche latin de Jérusalem. Créé en 1099 pendant les croisades, le patriarcat latin a été rétabli en 1847. L’Église latine compte un grand nombre d’ordres et de congrégations (102 en 2018), souvent d’origine française et italienne. Elle gère de nombreuses institutions éducatives et sociales. Le patriarche de l’Église grecque melkite catholique se fait représenter à Jérusalem par un évêque avec le titre de protosyncelle, ayant juridiction sur la ville sainte et les territoires palestiniens. Les syriens catholiques et les arméniens catholiques ont tous les deux un exarque siégeant à Jérusalem. Les maronites vivent surtout dans le Nord d’Israël et c’est donc à Haïfa que réside leur évêque.
Les arméniens orthodoxes sont représentés à Jérusalem par un patriarche et un nombre de croyants inférieur à 1500. Ils se composent de trois éléments : les « anciens » arméniens de Terre Sainte, les descendants des réfugiés arméniens survivants du Génocide lors de la Première Guerre mondiale, et les immigrés arméniens venus après la chute de l’Union soviétique. Les arméniens vivent surtout dans leur quartier de la vieille ville et à Jérusalem-Ouest. Ils entretiennent des contacts avec la population palestinienne ou juive selon leurs préférences et leur lieu d’habitation. La plupart des arméniens venus avant 1948 se sentent solidaires des aspirations palestiniennes. L’organisation du patriarcat arménien repose avant tout sur la Confrérie de Saint Jacques et sur un conseil composé de dignitaires religieux appartenant à l’intérieur et à l’extérieur de la Terre Sainte.
Les syriaques et les coptes orthodoxes ont chacun un métropolite à Jérusalem. Depuis le milieu du XIXe siècle, l’Église copte se dispute avec l’Église éthiopienne la propriété du monastère de Deir al-Sultan située près du Saint-Sépulcre. La communauté éthiopienne a longtemps été composée d’un petit nombre de familles qui se retiraient dans les lieux saints afin de mener une vie de prière. En raison des bonnes relations politiques entre Israël et l’Éthiopie, un nombre important de travailleurs immigrés viennent en Israël et, depuis quelques années, de plus en plus de réfugiés. Les Éthiopiens vivent autour des monastères éthiopiens de Jérusalem-Ouest et de la vieille ville où ils se mêlent aussi bien avec les Juifs qu’avec les Arabes. Ils constituent ainsi une particularité parmi les chrétiens orientaux de Terre Sainte.
L’origine des évêchés épiscopal et luthérien remonte à un évêché commun anglican-luthérien, créé en 1841 par un accord entre la Grande-Bretagne et la Prusse. Cette dernière décidant de quitter l’union des Églises en 1886, l’Église anglicane en garde seule l’évêché. Aujourd’hui, la compétence de l’archevêque épiscopal de Jérusalem couvre la Palestine, Israël, la Jordanie, le Liban et la Syrie. La communauté luthérienne allemande a suivi sa propre voie, indépendamment de l’évêché anglican de Jérusalem, ses activités étant soutenues par le Jerusalemverein (Association de Jérusalem), créé à Berlin en 1853. Jusqu’à la Première Guerre mondiale, l’empereur Guillaume II a soutenu l’association et s’est lui-même rendu en Terre Sainte en 1898. À cette occasion, il a inauguré l’église protestante allemande du Rédempteur dans la vieille ville de Jérusalem. À la suite de ce voyage, est créée la fondation de l’impératrice Auguste Victoria, sur le Mont des Oliviers. La communauté évangélique arabe est issue, pour une part importante, de sortants de « l’Orphelinat syrien » de la famille Schneller. En 1929, naît la communauté évangélique palestinienne de Jérusalem, restée pourtant étroitement liée à la communauté luthérienne allemande. En 1958, se constitue l’Église luthérienne sous le nom d’Église évangélique luthérienne de Jordanie (Evangelical-Lutheran Church of Jordan, ELCJ) qui sera dirigée dès 1979 par un évêque dont le siège sera à Jérusalem.
La situation œcuménique à Jérusalem est considérée comme l’une des pires au monde. Des conflits sur les privilèges des Églises quant aux lieux saints ralentissent le rapprochement œcuménique. Un facteur extérieur rapproche pourtant les Églises de Terre Sainte l’une de l’autre depuis les années 1980 : la menace de « l’israélisation » de la ville sainte qui a forcé les chefs d’Églises de se montrer unis. Depuis de longues années, ont-ils pris l’habitude de publier des déclarations communes.
L’Assemblée des ordinaires catholiques de Terre Sainte a promulgué, en 2021, des directives œcuméniques. Elles visent surtout la participation des fidèles à la vie sacramentelle et prennent en considération la situation interconfessionnelle de beaucoup de familles chrétiennes. Sur le plan spirituel, on célèbre, à la fin janvier de chaque année, la semaine de l’unité des chrétiens par des prières communes, offertes à tour de rôle dans les églises de toutes les communautés chrétiennes. La situation exceptionnelle de la pandémie COVID-19 en mars 2020, a même donné l’occasion de dire une prière interreligieuse pour le salut de tous. Y ont participé les représentants de plusieurs Églises, les grands rabbins ashkénaze et séfarade, ainsi que des représentants de l’islam et des Druzes.
Jérusalem – Destination des pèlerins du monde entier
Le patriarcat grec-orthodoxe s’occupe de l’accueil des pèlerins orthodoxes. Reste à souligner la position particulière de l’Église russe-orthodoxe qui gère à Jérusalem plusieurs églises, monastères et hospices pour pèlerins (le fameux Russian Compound près de la Jaffa Street à Jérusalem-Ouest et l’église russe au pied du Mont des Oliviers), établis depuis la fin du XIXe siècle par la Société impériale orthodoxe de Palestine (fondée en 1882, confirmée et réformée la dernière fois en 2003). La société défend en Terre Sainte les intérêts du patriarcat de Moscou et s’occupe des pèlerins russes.
Côté catholique, la majorité des lieux saints sont gardés par les Franciscains de la Custodie (établie par le pape Clément VI en 1342). Avec l’aide de frères de différents pays, la Custodie dirige une bonne partie de la pastorale de pèlerins catholiques qui pratiquent diverses langues. À souligner aussi l’engagement social très important de la Custodie envers les chrétiens de Jérusalem, surtout dans le secteur de l’habitation et des bourses d’études.
Les pèlerins des pays arabes se sont faits rares depuis l’occupation de Jérusalem-Est par Israël en 1967. Le pape copte-orthodoxe Chenouda III (1971-2012) a interdit à ses fidèles le pèlerinage à Jérusalem au moment où l’Égypte et Israël concluaient un traité de paix en 1979. Le pape Tawadros (2012-), après s’être lui-même rendu à Jérusalem en 2015 à l’occasion des obsèques du métropolite copte, a levé cette interdiction en janvier 2022. Suite à cette mesure, 5000 Égyptiens approximativement se sont rendus à Jérusalem pour les célébrations pascales de 2022. Les chrétiens palestiniens se félicitent de cette présence de coreligionnaires arabes et la considèrent comme un renforcement important de leur position dans la ville sainte. Les pèlerins jordaniens, de leur part, sont peu nombreux. Ils peuvent demander des visas de groupe pour visiter les lieux saints à Jérusalem, en Israël et dans les territoires palestiniens, mais très peu en font usage. Aux fidèles du Liban et de la Syrie, la visite des lieux saints reste interdite, l’état de guerre qui règne toujours entre leurs pays et l’État d’Israël interdit toute communication avec l’État juif et ceci malgré la visite pastorale du patriarche Béchara Raï auprès de la communauté maronite d’Israël en 2014.
Le service religieux, l’entretien des églises, la préservation des droits de propriété et l’assistance aux pèlerins constitue une part importante du caractère des Églises de Jérusalem. Les droits de propriété et les privilèges sont régis par le « statu quo » de 1757, modifié en 1852. Cette réglementation n’a pas été modifiée, notamment parce que les Églises veillent jalousement sur leurs droits et privilèges. Ainsi les Églises grecque-orthodoxe, catholique, arménienne, copte, syriaque et éthiopienne jouissent-elles de droits sur des parties spécifiques de l’église du Saint-Sépulcre. En revanche, la clé se trouve depuis des siècles entre les mains de deux familles musulmanes. Les grecs, les arméniens, les coptes et les syriaques se partagent la propriété de l’église de la Nativité à Bethléem. Les catholiques n’ont qu’un droit d’accès à la grotte de la Nativité située sous la basilique. Mais ils ont leur propre église, directement rattachée à l’église byzantine. Les conflits interconfessionnels ont nettement diminué depuis que les travaux de restauration et de conservation, exécutés en entente cordiale par les différentes Églises dans l’édicule du Saint-Sépulcre (2016-2017), la basilique de la Nativité (2013-2020) et sous les pavées de la rotonde du Saint-Sépulcre (2022-), ce qui a renforcé le sentiment de confiance et de solidarité.
La vie sociale et politique des chrétiens de Jérusalem
Statut légal
Les chrétiens arabes de Jérusalem, comme tous les Palestiniens de la partie orientale de la ville, peuvent avoir un passeport jordanien. De plus, 52 % des chrétiens palestiniens de la ville sont titulaires d’une carte d’identité israélienne leur permettant la résidence permanente à Jérusalem, statut spécial accordé aux Palestiniens de Jérusalem après l’occupation israélienne de la ville en 1967. Depuis 2005, 44 % des chrétiens ont obtenu, en plus de cela, la citoyenneté israélienne (en 2005, seulement 5 % l’avaient). Ils hésitent donc entre leurs espoirs d’une future autonomie palestinienne dans Jérusalem-Est et les avantages que leur offre l’État juif. La citoyenneté israélienne leur offre l’accès au régime d’assurance nationale, au système de soins de santé, aux allocations de chômage et d’invalidité et aux prestations de retraite. Le choix de la citoyenneté israélienne n’est donc pas nécessairement lié à un changement d’opinion politique.
Les options de mariage des chrétiens de Jérusalem sont limitées par la loi israélienne, dite de « regroupement familial », promulguée en 2003. Cette loi empêche les familles non-juives d’obtenir des droits de résidence et d’entrée à Jérusalem. Elle porte également préjudice aux enfants nés dans les territoires palestiniens de parents résidant à Jérusalem-Est. Environ 300 familles chrétiennes de Jérusalem ont souffert de cette loi, en particulier les couples mariés après mai 2002. Il faut savoir que 16 % des familles chrétiennes de Jérusalem ont un parent originaire de Cisjordanie, principalement de Bethléem et de Ramallah. La loi restreint, de plus, les possibilités des chrétiens de Jérusalem de conclure des mariages avec un partenaire de la Cisjordanie. Étant donné les relations étroites entre familles chrétiennes hiérosolymitaines et bethléemites, cela est ressenti comme très douloureux et constitue une raison importante pour l’émigration des chrétiens. De nombreuses organisations internationales, israéliennes et palestiniennes, de défense des droits de l’homme ont fait pression contre cette loi, y compris la Société de Saint Yves (organisation de défense des droits de la personne sous les auspices du Patriarcat latin de Jérusalem) [12][12]Akroush, Jerusalem Christian Youth, 2019, p. 16..
La famille chrétienne
Depuis 2012, on constate une baisse du nombre de mariages chrétiens. Entre 2012 et 2019, on compte en moyenne chaque année 25 à 30 nouveaux mariages. L’âge médian des mariés chrétiens est de 29,2 ans pour les hommes et de 25,6 ans pour les femmes (données de 2016). 37 % de familles chrétiennes ont trois enfants, 31 % en ont quatre et 17 % deux. En comparant le taux de fécondité, les chrétiens ont le taux de fécondité le plus bas. Par conséquent, la communauté chrétienne de Jérusalem est, en moyenne, nettement plus âgée que la communauté musulmane (38 % des musulmans ont moins de 15 ans par rapport à 21 % des chrétiens). Quant aux personnes âgées (65 ans et plus), elles représentent 4 % de la population musulmane contre 14 % de la population chrétienne. L’âge médian dans la communauté chrétienne est de 34 ans, contre 21 ans dans la communauté musulmane.
La plupart des familles chrétiennes se présentent comme appartenant à la classe moyenne (90 %). Ceux qui s’identifient comme pauvres s’élèvent à 7 %. Dans plus de la moitié des familles chrétiennes (55 %), les deux parents travaillent, tandis que 44 % des familles n’ont qu’un seul soutien de famille, le plus souvent, c’est le père.
Les chrétiens arabes de Jérusalem vivent surtout en trois zones : au centre (vieille ville, Ras al-Amoud, Beit Faji), au Nord (Kufur Aqab, Anata, Beit Hanina, Shufat) et au Sud (Beit Safafa, Sharafat, Tantur). De plus en plus de familles chrétiennes achètent des propriétés dans les quartiers juifs, comme à Pisgat Ze’ev, ou acceptent de loger dans de nouveaux quartiers périphériques comme Talpiot-Est et Gilo. 30 % des familles chrétiennes sont propriétaires de leur appartement, 48 % vivent dans des appartements loués, tandis que 22 % habitent dans des propriétés « protégées » d’Église. Ces chiffres sont inquiétants si l’on considère que le taux d’accès à la propriété en Israël est de 66,5 %. Les coûts de loyer peuvent atteindre jusqu’à 40 % du revenu mensuel d’une famille, ce qui en fait la plus grande charge financière. Si l’on tient compte de tous les facteurs, on peut affirmer que plus de 60 % des familles chrétiennes sont menacées et vivent sous le seuil de la pauvreté. Elles peuvent à peine finir le mois sans dettes ou sans aide sociale de la part des Églises et des organisations caritatives.
Ainsi, près de 500 familles chrétiennes de Jérusalem reçoivent une aide financière sous diverses formes au moins une fois par an. Un quart des jeunes chrétiens reçoivent une aide financière de leurs Églises soit dans le cadre d’un programme d’aide sociale, soit sous la forme d’une aide aux études fournie par les Églises ou les écoles. La Custodie de Terre Sainte est le principal fournisseur de bourses d’études, offrant environ 40 bourses chaque année. Le patriarcat grec-orthodoxe offre plusieurs bourses d’études par an par le biais de l’école Saint Dimitri, mais pas nécessairement à des chrétiens. La Société de Saint-Vincent de Paul offre une dizaine de bourses d’études pour la formation professionnelle ou l’accueil de chrétiens pauvres. Le Secrétariat de solidarité, institution de l’Église catholique, offre des aides pour les frais de scolarité à plus de 2000 élèves chrétiens à Jérusalem, en Palestine, en Israël et en Jordanie.
Les écoles chrétiennes
La grande majorité des étudiants chrétiens de Jérusalem (98 %) sont inscrits dans des écoles chrétiennes. Cependant, on observe une tendance croissante parmi les Palestiniens – y compris les chrétiens – à s’inscrire dans les écoles gouvernementales israéliennes afin d’être mieux préparés au marché du travail israélien.
Les Églises et les organisations qui leur sont liées gèrent douze écoles à Jérusalem qui accueillent 1660 élèves chrétiens et plus de 5500 élèves musulmans. Huit de ces douze écoles sont situées dans et autour de la vieille ville. Les écoles chrétiennes sont le seul endroit où musulmans et chrétiens passent du temps ensemble, où ils peuvent faire connaissance au-delà de rencontres courtes et banales de tous les jours. Les écoles chrétiennes ont donc la responsabilité de promouvoir la coexistence, l’acceptation de l’autre et la démocratie, et d’enseigner l’histoire de la Terre Sainte dans une perspective chrétienne (y compris la période byzantine), ce qui ne fait partie ni du curriculum des écoles publiques israéliennes ni palestiniennes.
Par rapport aux autres écoles privées, municipales et islamiques (awqâf), les écoles chrétiennes jouissent d’une excellente réputation en termes de qualité de l’enseignement et en vue des certifications proposées, tant sur le plan local qu’international. Toutes les écoles chrétiennes suivent le programme palestinien, au moins jusqu’à la sixième année, avant de décider de s’engager ou dans le Tawjihi palestinien ou dans d’autres programmes tels que le General certificate of education (GCE) britannique, l’Abitur allemand (Schmidt’s Girls College), ou le Bagrut israélien. Les manuels palestiniens utilisés sont pourtant très déficitaires quant à la présentation des religions autres que l’islam et des périodes historiques anté-islamiques de la Palestine. Un rapport inédit du Centre œcuménique de théologie de la libération – Sabeel déplore que le curriculum palestinien qualifie chrétiens et juifs d’infidèles, qu’il préconise un califat islamique et qu’il insiste sur le port du hijab ou robe islamique. Un autre problème du système scolaire à Jérusalem-Est, y compris pour les écoles chrétiennes : à la fin de leurs études scolaires, à peine un tiers de chrétiens peuvent communiquer en hébreu alors que cette langue est la seule langue officielle dans les bureaux gouvernementaux et municipaux qui contrôlent tous les aspects de la vie à Jérusalem et en Israël.
En plus de leur rôle éducatif essentiel, les écoles chrétiennes sont sans doute les meilleurs forums pour la coexistence et la paix civile entre musulmans et chrétiens. Les musulmans qui étudient dans les écoles chrétiennes sont considérés comme les véritables agents de changement aux côtés de leurs concitoyens chrétiens. Les écoles chrétiennes s’investissent ainsi dans le développement d’êtres humains moralement responsables, et forment les meilleurs leaders de la société, démocratiques, énergiques et d’esprit ouvert quelle que soit leur croyance. Grâce à leur plus grande ouverture sur le monde vu le caractère international des congrégations religieuses ou institutions qui les soutiennent, les écoles chrétiennes de Jérusalem jouissent d’une plus grande liberté d’enseignement et vont au-delà des seuls textes éducatifs pour proposer à leurs étudiants des modèles de citoyenneté et des pratiques sociales et politiques qui favorisent la coexistence et la solidarité intercommunautaires.
Les Églises et leurs services
Malgré le nombre modeste de fidèles, les Églises en tant qu’institutions sont très fortes, grâce à la solidarité de l’Église universelle. Cela concerne les secteurs d’éducation, santé, culture, protection sociale et développement. Sur le plan culturel, il faut mentionner les nombreux centres communautaires, les clubs et les scouts, tous les trois régulièrement organisés selon les appartenances confessionnelles. Le secteur de la santé aussi joue un rôle important dans l’engagement des Églises qui gèrent cinq hôpitaux dans la ville sainte dont le plus grand est l’hôpital Auguste Victoria, géré par la Fédération luthérienne mondiale. Ces institutions emploient un total de 1200 salariés et accueillent plus de 330 000 patients par année, toute appartenance religieuse confondue.
Quant au secteur de la protection sociale, il concerne l’accueil et la réhabilitation de personnes handicapées, l’aide sociale, l’accueil de personnes âgées et la défense des droits de l’homme. À mentionner en particulier la Greek Orthodox Benevolent Society, le Good Samaritan Eldery Center situé dans un immeuble de la vieille ville appartenant au patriarcat grec-orthodoxe mais à vocation œcuménique, le foyer de personnes âgées des Sœurs de Notre Dame des Douleurs à Jérusalem-Est, les activités sociales de la Société de Saint Vincent de Paul, de Caritas Jérusalem et finalement la Société de Saint Yves pour la défense des droits de la personne (patriarcat latin de Jérusalem). Finalement, il faut mentionner les organisations internationales de développement à vocation chrétienne qui ont des branches ou bureaux à Jérusalem. Je ne peux conclure ce chapitre sans faire mention du Christian Information Center, tenu par la Custodie de Terre Sainte des Franciscains. Le centre s’occupe de la production médiatique, la distribution d’informations et de nouvelles sur tout ce qui concerne la vie chrétienne à Jérusalem, en Palestine et en Israël.
La vie des chrétiens en Israël et Palestine
Israël
L’image des chrétiens de Jérusalem serait incomplète sans un regard sur les chrétiens dans les territoires palestiniens et en Israël. Environ 127 000 chrétiens palestiniens vivent dans l’État d’Israël (sans Jérusalem-Est). La majorité d’entre eux vivent en Galilée, à Haïfa et dans les villes de Jaffa, Ramla et al-Ludd. Ils appartiennent majoritairement aux Églises grecques-melkites catholiques, grecques-orthodoxes et latines. Dans le Nord, il y a également quelques maronites. Ils jouissent de la citoyenneté israélienne et donc, en principe, des mêmes droits politiques et sociaux que ceux des israéliens juifs. Toutefois, en raison de diverses dispositions administratives subtiles, les localités majoritairement arabes d’Israël n’ont pas le même accès aux ressources financières du gouvernement que les municipalités juives. Néanmoins, la plupart des Palestiniens chrétiens se sont accommodés de l’État juif, apprécient les acquis sociaux, profitent de la situation économique d’Israël et jouissent de la liberté de voyager avec un passeport israélien. Ils s’engagent dans les partis arabes israéliens, sans pourtant se sentir liés, dans les élections, aux partis arabes. Ils votent aussi, selon les circonstances politiques, pour des partis majoritairement juifs de gauche et de droite, voire dans certains cas pour des partis juifs résolument religieux. Le processus d’intégration des chrétiens de Galilée dans l’État juif a commencé dès les années 1960. Aujourd’hui, rares sont les chrétiens de Galilée qui souhaiteraient échanger leur citoyenneté israélienne contre l’intégration dans un État palestinien, malgré la méfiance croissante de la population juive à l’égard des chrétiens à cause de la présentation biaisée du christianisme dans les écoles qui mettent un accent particulier sur la persécution des juifs dans les pays « chrétiens » pendant le Moyen-Âge et dans l’époque moderne et qui ne distinguent pas entre les chrétientés d’Occident et d’Orient. De nombreux chrétiens israéliens arabes sont préoccupés aussi par la propagation des idées islamistes au sein d’une partie de la population musulmane d’Israël. Cela a entraîné un fort recul de l’engagement politique commun entre chrétiens et musulmans. Les conflits entre musulmans, chrétiens et druzes sont également de plus en plus fréquents.
Au côté des chrétiens arabes d’Israël – et presque sans contact avec eux – vivent environ 420 000 Israéliens chrétiens de langue hébraïque. Ils sont principalement originaires des pays de l’ex-Union soviétique ainsi que des pays d’Europe de l’Est. La plupart d’entre eux sont russes orthodoxes. Ils sont tous citoyens israéliens et pleinement intégrés dans la société juive. S’y ajoutent environ 160 000 migrants chrétiens, dont beaucoup de femmes. Ceux-ci se composent de travailleurs migrants légaux et illégaux, originaires principalement d’Asie (Philippines, Inde, Sri Lanka) ; de demandeurs d’asile (surtout en provenance d’Érythrée et d’Éthiopie) ; de personnes qui, à la recherche d’un emploi, sont entrées avec un visa touristique déjà expiré (principalement d’Europe de l’Est, notamment de Roumanie et d’Ukraine). Les juifs convertis au christianisme constituent un groupe minuscule. Les chrétiens non-arabes installés de manière permanente en Israël représentent aujourd’hui environ un quart de la population chrétienne. Si l’on ajoute les travailleurs migrants et les demandeurs d’asile qui ne vivent que temporairement en Israël, ce groupe est même numériquement plus important que celui des chrétiens arabophones. Le plus grand groupe de migrants vit à Tel Aviv. C’est là qu’a été ouverte en 2015 une nouvelle église catholique avec un centre social pour les communautés de migrants. À Jérusalem, les migrants catholiques sont accueillis au centre « Ratisbonne » dans l’Ouest de la ville. De nombreuses communautés protestantes et évangéliques sont également actives en Israël. Leurs églises et lieux de culte sont souvent installés dans des magasins, des appartements et des abris anti-bombardement.
Les chrétiens représentent aujourd’hui près de 2 % de la population de l’État d’Israël (Jérusalem comprise). Si l’on y ajoute les migrants, ce chiffre atteint presque 4 %. Les juifs constituent 75 % de la population et les musulmans 18 %.
Telle est la complexité du christianisme en Israël. La loyauté envers l’État d’Israël, très répandue parmi les arabes chrétiens d’Israël, est régulièrement mise à l’épreuve. Les Palestiniens, chrétiens et musulmans de Cisjordanie, voient confirmé en ces occasions leur rejet par et de l’État juif. À titre d’exemple, citons la loi sur la nationalité adoptée par le Parlement israélien en 2018. Cette loi réaffirme le caractère juif de l’État, mais va encore plus loin en attribuant le droit à l’autodétermination nationale au seul peuple juif. Selon la nouvelle loi, la langue officielle est uniquement l’hébreu. L’arabe, qui est langue officielle depuis 1948, n’a plus qu’un statut particulier non défini. Certes, les conséquences pratiques de la loi sont marginales, puisqu’elle ne fait que confirmer ce qui va de soi dans l’esprit de la plupart des Juifs d’Israël. Elle n’en a pas moins un caractère hautement symbolique. C’est pourquoi elle a été vivement critiquée par les chefs d’Églises.
En mai 2021, le conflit déclenché par les expulsions de maisons palestiniennes dans le quartier arabe de Sheikh Jarrah à Jérusalem-Est et l’intervention musclée des forces de sécurité israéliennes lors de cérémonies du mois de Ramadan à la mosquée al-Aqsa ont profondément divisé les Juifs et les Arabes d’Israël. Du côté juif, on a eu peur des attaques de roquettes du Hamas. Du côté arabe, on était solidaire des victimes civiles des contre-attaques israéliennes à Gaza et des familles palestiniennes de Jérusalem-Est chassées de leurs maisons. Dans les villes mixtes d’Israël, où cohabitent Israéliens juifs et arabes, cela a donné lieu à de violentes émeutes et à des attaques lynchiennes de la part d’extrémistes juifs et arabes. Les gens des deux côtés avaient peur. Les chrétiens arabes d’Israël se sont retrouvés une fois de plus pris entre deux feux : solidarité avec le peuple palestinien dont ils font partie et loyauté envers l’État d’Israël, au sein des frontières dans lesquelles ils vivent. Les résultats des élections en Israël qui donnent des suffrages de plus en plus extrêmes et les annonces du gouvernement mises en place en décembre 2022 ne laissent présager rien de bon pour l’avenir de la cohabitation entre israéliens juifs et arabes de même que pour l’intégration des chrétiens arabes en Israël.
Palestine
Regardons encore la situation des chrétiens en Palestine, c’est-à-dire dans les territoires de Cisjordanie, administrés par l’Autorité palestinienne de Mahmoud Abbas, et dans la bande de Gaza, dirigée par un gouvernement Hamas. Y vivent environ 43 500 chrétiens (en 2008, des chiffres plus récents ne sont pas disponibles), dont moins de 1000 à Gaza. La population chrétienne de Cisjordanie se concentre dans la région de Bethléem avec Beit Jala et Beit Sahour ainsi qu’à Ramallah et dans les villages environnants. En Cisjordanie, les chrétiens représentent 1,5 % de la population parmi 98,5 % de musulmans. Dans la bande de Gaza, les chrétiens sont une infime minorité de moins de 0,1 % parmi une population presque entièrement musulmane. Les chrétiens sont pleinement intégrés dans la vie palestinienne et considèrent, pour la très grande majorité, l’État d’Israël et ses forces de sécurité comme des occupants. Ils souffrent beaucoup du blocus imposé par le mur de séparation qui coupe des territoires israéliens, les territoires contrôlés par l’Autorité palestinienne. De plus, les nombreux check-points israéliens font de la Cisjordanie « un patchwork » et rendent extrêmement long et compliqué le transport d’un endroit à l’autre. Dans ces conditions, les visites familiales, notamment aux nombreux chrétiens palestiniens vivant à Jérusalem, ne sont guère possibles, tout comme un contrat d’emploi en Israël. La bande de Gaza est même totalement isolée. De nombreux chrétiens de Palestine attribuent à la persistance du conflit israélo-palestinien, l’islamisation toujours plus poussée de la société palestinienne et de l’influence croissante de groupes islamistes extrémistes qui leur font peur.
Conclusions
Les Églises de Jérusalem peuvent-elles jouer un rôle de médiatrice pour la paix ? Le conflit au Proche-Orient n’est certes pas uniquement un conflit religieux. Mais les deux parties justifient leurs revendications en référence aux textes sacrés. Le conflit ne se comprend ni ne peut être résolu sans l’interférence de la religion. Certes, les référents religieux, du côté israélien et du côté palestinien ne sont pas les seuls, mais l’importance des revendications basées sur les arguments séculiers va en diminuant. Au cours des trois dernières décennies, l’essor du mouvement nationaliste religieux des colons juifs et la montée en puissance du Hamas, ont pris une ampleur angoissante. Cela ne manque pas d’avoir des répercussions sur la cohésion des Palestiniens chrétiens et musulmans. En fait, sans une participation constructive des religions, c’est-à-dire des leaders religieux et des organisations basées sur la foi religieuse, les tensions ne sauraient diminuer.
Quel rôle les Églises peuvent-elles jouer ? Au niveau mondial, les positions des Églises vis-à-vis du conflit israélo-arabe, sont loin d’être les mêmes. Beaucoup de chrétiens évangéliques américains soutiennent les revendications sionistes. Les Églises des pays arabes défendent le droit des Palestiniens. Le Vatican insiste sur le droit international et la décision de partage de l’ONU qui remonte à 1947. Il défend la position selon laquelle seuls Palestiniens et Israéliens ensemble peuvent parvenir à une autre solution par la voie de la négociation. Et l’Église de Jérusalem ? Elle aussi représente divers courants chrétiens : des chrétiens palestiniens en Palestine, des chrétiens arabes en Israël et des chrétiens de langue hébraïque en Israël, qui ont, chaque groupe pour sa part, des perspectives très différentes.
L’Église locale se trouve de plus en plus dans une situation de tension partagée entre les attentes des chrétiens de Palestine et de Jérusalem-Est d’une part et celles des chrétiens d’Israël d’autre part. Alors qu’en Palestine on attend que l’Église défende avec force les intérêts des Palestiniens, qu’elle dénonce les injustices et les violations du droit international, les Arabes israéliens s’identifient de plus en plus à l’État d’Israël et à ses réalisations sociales et économiques. La montée du Hamas et d’autres groupes islamistes à Gaza montre que les Églises pourraient jouer le rôle de médiateur. Les Églises doivent apprendre à gérer cette tension et les attentes divergentes de leurs fidèles. Elles pourraient ainsi jouer un rôle important de précurseur. La condition préalable est toutefois que les fossés confessionnels, particulièrement profonds en Terre Sainte pour des raisons historiques, soient enfin surmontés et que les Églises chrétiennes parviennent à une vraie entente œcuménique.

"""
    prompt = """Résume le texte ci-dessous en français. Le résumé doit faire environ 10% de l'article d'origine.
Output language: french
Text: $text
"""

    parameters = DeepInfraOpenAICompletionParameters(
        # model = "cognitivecomputations/dolphin-2.6-mixtral-8x7b",
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=512,
        completion_altText=None,
        prompt=prompt,
    )
    processor = DeepInfraOpenAICompletionProcessor()

    docs = processor.process([Document(text=text)], parameters=parameters)
    assert "Jerusalem" in docs[0].text


@pytest.mark.skip(reason="Not a test")
def test_explain_label():
    prompt = """Vous êtes un expert en classification de texte. Votre tâche consiste à fournir une explication en une phrase pour chacun des types d'événements décrits dans le texte en entrée.
La sortie doit être une table au format markdown dont la première colonne contient le type d'événement et la seconde colonne l'explication associée. Si aucun événement n'a été détecté, la sortie doit juste être "Aucun événement"
{%- set labels=[] -%}
{%- for cat in doc.categories -%}
  {%- do labels.append('"' + cat.label + '"') -%}
{%- endfor %}
{% if labels|length > 0 %}
Types d'événements à décrire: {{ labels|join(', ') }}
{%- else %}
Types d'événements à décrire: aucun
{%- endif %}
Texte: {{doc.text}}
    """
    parameters = OpenAICompletionParameters(
        model=OpenAIModel.gpt_3_5_turbo,
        completion_altText="explicationGPT",
        max_tokens=1024,
        prompt=prompt
    )
    processor = OpenAICompletionProcessor()

    parameters2 = DeepInfraOpenAICompletionParameters(
        model="cognitivecomputations/dolphin-2.6-mixtral-8x7b",
        completion_altText="explicationMixtral",
        max_tokens=1024,
        prompt=prompt,
    )
    processor2 = DeepInfraOpenAICompletionProcessor()

    testdir = Path(__file__).parent
    source = Path(
        testdir,
        "data/event_detection-document-test.json",
    )
    with source.open("r") as fin:
        jdoc = json.load(fin)
        doc = Document(**jdoc)
        docs = processor.process([doc], parameters)
        doc1 = docs[0]
        assert doc1.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
        doc = Document(**jdoc)
        docs = processor2.process([doc], parameters2)
        doc2 = docs[0]
        assert doc2.altTexts == IsList(HasAttributes(name=parameters.completion_altText))
