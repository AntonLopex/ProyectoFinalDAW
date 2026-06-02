import io
import uuid

from flask import flash, jsonify, redirect, render_template, request, url_for
from datetime import datetime

from sqlalchemy.orm import joinedload
from extensions import db
from flask_login import current_user, login_user

from forms.adminForms.proveedor_form import UsuarioProveedorForm
from models.acompanante import Acompanante
from models.enums import EstadoStandEnum, TipoVCEnum
from models.historial_stand import HistorialStand
from models.producto import Producto
from models.solicitud import Solicitud
from models.stand import Stand
from models.mobiliario import Mobiliario
from models.detalle_solicitud_mobiliario import DetalleSolicitudMobiliario
from models.detalle_solicitud_stand import DetalleSolicitudStand
from models.usuario import Usuario
from models.extra import Extra
from models.config import Config
from utils.utils import comprobarContraseña, correo_confirmacion_registro, createUsername, generar_qr_imagen_64, inject_year, registrar_historial
 
from flask import jsonify, current_app
from flask_login import current_user
from flask_mail import Message
import os
 
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from extensions import mail



# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD Y REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del dashboard del proveedor, mostrando la información relevante para el proveedor en su página principal
def f_proveedor():
    config = Config.query.first()
    return render_template("proveedor/proveedor.html", now=datetime.now(), config=config)

# Array asociativo de proveedores con sus codigos de DSG
PROVEEDORES = {
    30449: "GRUPO ARMARIOS PERSIANA, S.A. (GAPSA)",
    30000: "DISTRISANTIAGO PAPELERIA, S.L.",
    30001: "ALMACEN",
    30963: "QUILOSA",
    30458: "MANIPULADOS MARIOLA, S.L.",
    30515: "INCLASS MOBLES, S.L.",
    30966: "FISICO Y POLITICO, S.L.",
    30388: "SALVADOR GARCIA, S.L.",
    30964: "DISTRIBUIDORA PAPELERA, S.A.**",
    30510: "IBERBARNA PAPEL, S.A.**",
    30511: "C.S.A.G. PAPEL, S.A.**",
    50000: "ALMACEN OFIREYCO",
    30471: "INFORPOR, S.L.",
    30978: "INDUSTRIAL PAPELERA ANDINA, S.L.",
    30188: "TEMPEL, S.A.",
    30195: "COFRAP ESPAÑOLA, S.A. (MAPED)",
    30362: "CHARMEX INTERNACIONAL, S.A.",
    30430: "NADAL 1987, S.L.",
    30035: "NAIPES HERACLIO FOURNIER, S.A.",
    30240: "MITSUBISHI PENCIL ESPAÑA, S.A.",
    30143: "GLOBOLANDIA, S.L.",
    30189: "INDUSTRIAS SARO, S.L.",
    30148: "FRAGA IMPORT S.L",
    30158: "ARCONVERT, S.A. (DIVISION SADIPAL)",
    30173: "APLI PAPER, S.A.U.",
    30180: "GRAFOPLAS DEL NOROESTE, S.A.",
    30181: "PALMERA",
    30242: "SUCESORES DE VDA. E. FAJEDA",
    30246: "COMERCIAL ANTONIO GARRIGA, S.A.",
    30253: "DOHE, S.A.",
    30262: "SENFORT, S.A.",
    30263: "LOAN INDUSTRIAS GRAFICAS, S.L.",
    30268: "CYP BRANDS EVOLUTION, S.L.",
    30025: "CARCHIDEA, S.L.",
    30026: "ESSELTE, S.A.",
    30029: "CARLOS WENDEL, S.L.",
    69: "MEDIABOX-PRODUCAO MULTIMEDUA LDA.",
    30412: "YOSAN",
    30418: "BONIFACIO, S.A.",
    31056: "SOLUCIONES Y FORMAS, S.L.",
    31205: "ARTE Y CERAMICA DE GALICIA, S.L.",
    31292: "AGSA REGALOS DE EMPRESA, S.L.",
    70010: "SUMINISTROS INEC, S.L.L. ****",
    30586: "THE NAVIGATOR COMPANY, S.A.",
    30563: "LOBA MANUALIDADES",
    31119: "TORCULO ARTES GRAFICAS, S.A.",
    30950: "LOGA COLAS Y ADHESIVOS INDUSTRIALES",
    31220: "SOC. TRANSF. DE PAPEIS VOUGA, LDA",
    31224: "DOUBLET IBERICA, S.A.",
    31190: "CASIO ESPAÑA, S.L.",
    30594: "ARTICULOS PAPELERIA SENA, S.L.",
    31020: "UFP ESPAÑA, S.A.",
    30561: "HAMELIN BRANDS, S.L.U.",
    71001: "DISTRISANTIAGO PORTUGAL C. E R., LDA.",
    70007: "DISTRISANTIAGO PAPELERIA, S.L.",
    31194: "IMPRENTA BRASIL, S.L.",
    70001: "MCD CONSUMIBLES, S.L.",
    31283: "HERGO SILLERIA, S.L.",
    30527: "XALLAS FLEJES Y SUMINISTROS DEL EMB., SL",
    70004: "ADIMPO, S.A.",
    71000: "FRAMOMOTORS, S.L.",
    31082: "COTELGA, S.L.",
    31098: "ESPRINET IBERICA, S.L.U.",
    30518: "GENERAL DE PILAS, S.L.",
    31105: "DMI COMPUTER, S.A.",
    30565: "ARGUVAL, S.L.",
    10005: "DISTRISANTIAGO PAPELERIA, S.L.",
    31258: "DARLIM, S.L.",
    31352: "GRUPO ERIK EDITORES, S.L.",
    31376: "ARCAS OLLE, S.L.",
    31397: "COLOP ESPAÑA, S.L.",
    31385: "STABILO INTERNACIONAL GMBH",
    31387: "ELSI POS TECHNOLOGY",
    31412: "MANIPULADOS DEL PAPEL MARTINEZ, S.L.",
    31395: "VINITRADING, S.L.",
    31413: "3M ESPAÑA. S.L.",
    31414: "NOVUS DAHLE GMBH",
    31415: "EDICIONS ADDITIO, S.L.",
    31377: "TRADEXBAL SOLUTIONS, S.L.",
    31390: "UPM RAFLATAC GMBH (GLOBAL NOTES)",
    31418: "LES PUNXES DISTRIBUIDORA, S.L. (TOMBOW)",
    31382: "MOLIN-ESTILOGRAFICA S.L.",
    31383: "MOBLES GRAU S.A.",
    31423: "ALTELED",
    31367: "LEROY MERLIN ESPAÑA, S.L.U.",
    31455: "SCRIBERE & DISCERE S.L. (LAMELA)",
    31432: "TARIFOLD, S.A.S.",
    31456: "ENRIQUE RUBIO POLO, S.L.",
    31458: "MEPEL S.L.",
    31419: "DYMCO",
    31320: "LUMINOSOS TOLTECH, S.L.",
    31381: "EXADI BUSINESS, S.L. (ARCYRIS PRINT)",
    31446: "CELORAMA S.L.",
    31422: "MINK BLAU, S.L. (TOMBOW ALEMANIA)",
    31405: "EDICIONES REBOST DEL PAPER",
    31512: "GLOBAMAS, S.L. (ORIGINAL USB)",
    31527: "RUIFERPA, S.L.",
    31526: "HP PRINTING AND COMPUTING SOLUTIONS SLU",
    31621: "UNECOL ADHESIVE IDEAS, S.L. (SUPERTITE)",
    31612: "INNOVACION E INVESTIG. S.L. (TOUCAN ECO)",
    31604: "LINUX TECHNOLOGY S.L. (VISIONPUBLI)",
    31619: "PORTOMEDICA, S.L.",
    31620: "IFULI, S.L.",
    31596: "PIGOCIA, S.L.",
    31524: "RAMIREX PLASTICOS AGUEDA, LDA",
    31525: "TWINCO SOLUTION APS",
    31598: "EXACLAIR, S.A. (CLAIREFONTAINE)",
    31611: "PLASTIPARR PADRON, S.C.",
    31603: "FOLDER PAPELERIAS, S.A.",
    31605: "TESIS GALICIA, S.L.",
    31515: "GSI DOTACION INDUSTRIAL, S.L.",
    31597: "YEARNTREE LTD (DEFLECTO)",
    31529: "GO EUROPE GMBH (OLYMPIA)",
    31519: "TOYS SERVICE, S.L. (ANDREU TOYS)",
    31622: "CEP OFFICE SOLUTIONS",
    31530: "SISTEMAS DE PAPEL CONTINUO, S.L.",
    31618: "MORAVIA CONSULTING, SPOL. S R.O.",
    31595: "TRUST SPAIN S.A.",
    31593: "FABRI-PAPEL, S.L.U.",
    31615: "EXACLAIR, S.A. (QUO VADIS)",
    31528: "PENSFROMBCN, S.L. (INOXCROM)",
    31602: "ARTESANIA CERDA S.L.",
    31616: "CARNERO BAZ, ALBERTO (TOMAS CARNERO)",
    31516: "EVOLIS S.A. (BADGY)",
    31522: "SANTOS PRINTING, S.L.",
    31520: "EXACLAIR, S.A. (PAPEL CLAIREFONTAINE)",
    31523: "EDICIONES DEUSTO, S.A. (BOOST ITALOAG)",
    31601: "SOLITIUM NOROESTE, S.L.U.",
    31600: "EUROPRINT METROPOLI, S.L.",
    31606: "GRAN FORMATO EUROPRINT, SL",
    31656: "MAGAZINUL DE PAPETARIE, S.R.L. (FOLDER)",
    31635: "NR MOBILITY SOLUTIONS, S.L.",
    31647: "DESYMAN",
    31646: "AVANTREE LIMITED",
    31630: "ARTEGALIA ECONOMICA SOCIAL (ALENTAE)",
    31637: "IMAGILAND, S.L.",
    31640: "MANOLITO BOOKS S.L.",
    31643: "APPLICATION DES GAZ S.A.S.",
    31623: "MIQUEL RIUS (APLI PAPER, S.A.U.)",
    31638: "2BEE2",
    31649: "TEB BARCELONA SCCL",
    31626: "COBO DE LUCAS, ALEJANDRO (COBO INDUSTRIA)",
    70011: "I & E FOREST PANELS, S.L.",
    31654: "SILVER SANZ, S.A.",
    31624: "M.HERMIDA INFORMATICA S.L.",
    31636: "FG2 LESMARC, S.L.",
    31648: "ADIEGO MARTINEZ, JOSE MANUEL",
    31627: "VIQUEL S.A.S.",
    31633: "OMNI TREND, S.L. (CROSS)",
    31644: "AGUILERA MARQUEZ, SERGIO",
    31625: "RAPESCO OFFICE PRODUCTS PLC",
    31645: "TORRES Y SAEZ, S.A.U.",
    31631: "EDICIONES SALDAÑA, S.A.",
    31642: "ETIROL S.L.",
    31628: "EMBALAJES COSTA VELLA, S.L. (XALLAS)",
    31629: "GRUPO FORMA 5, S.L.U.",
    30129: "UARCHIVO 2000, S.A.",
    30191: "INETA, S.A.",
    30333: "DISTRISANTIAGO PORTUGAL",
    30054: "HOFMANN, S.L.",
    30317: "MOLINER, DOMINGUEZ Y CIA., S.A.**",
    30086: "PRODUCTOS IMEDIO, S.A.",
    30087: "MULTI-TEC, S.A.",
    30088: "HENKEL IBERICA, S.A.",
    30048: "KRONOS, S.R.L.",
    30325: "ARMANDO SILVA, S.L.",
    30012: "SAFTA, S.A.",
    30015: "CABERO GROUP 1916, S.A.",
    30120: "INDUSTRIAL VERBENERA CASTELLONENSE, S.L.",
    30122: "STYB",
    30016: "POESSA",
    30017: "IBERPLAS, S.L.",
    30341: "INDUSTRIAS SOMOMAR, S.A.",
    30056: "UNIVERSAL ESPAÑOLA, S.A. (CARIOCA)",
    30057: "FRAMUN, S.A",
    30060: "BUENO HERMANOS S.A",
    30069: "COMERCIAL ARGE, S.A. (PILOT)",
    30093: "EUROPEA DE CINTAS, S.R.L.",
    30101: "MASATS COLORING, S.L.U.",
    30103: "FACTIS, S.A. (MILAN)",
    30107: "EDICROMO, S.A.",
    30110: "PAPELERA DE BRANDIA, S.A.",
    30113: "RENOLIT HISPANIA S.A ESTELLA",
    30002: "S.A.DE TALLERES DE MANIPULACION DE PAPEL",
    30004: "STAEDTLER IBERIA, S.A.",
    30007: "VARIOS FABRICANTES",
    30010: "FULCO, S.A. (JOVI)",
    30135: "PRYSE S.A",
    30040: "BIC IBERIA, S.A.U.",
    70003: "IGNIRE SOFTWARE EMPRESARIAL, S.L.",
    30463: "J. DOMINGO FERRER, S.L.",
    30553: "OLI-SERVI, S.L.",
    30498: "FELLOWES IBERICA, S.L.",
    30387: "A.S.DE MATERIAL O.DISNAK A.I.E.",
    70006: "GRAILANDIA ESPAÑA, S.A.",
    70959: "INFINITY SYSTEM, S.L.",
    30165: "PLANNING SISPLAMO, S.L.",
    31096: "DIGAMEL, S.A.",
    30245: "EUROPEA DE DISEÑO EURODIS, S.L.",
    30248: "R. BARREIRO EMBALAJES, S.L.",
    31019: "MEGABLOK, S.A.",
    30389: "TD SYNNEX SPAIN S.L. (TECH DATA)",
    30973: "CASH RECORD",
    70005: "INFORPOR, S.L.",
    70008: "DIVINITY INTERNACIONAL 21, S.L.",
    70009: "VERBRAUCH, S.L.",
    30168: "MANIPULADOS ZORRILLA",
    30454: "TIMBRADOS VALENCIA, S.L.",
    30983: "ART MATERIALS S.A. (ARTIST)",
    30380: "ROCADA, S.L.",
    30373: "KESTA, S.A.",
    30495: "CODEBIT SYSTEMS, S.L.",
    30111: "MAXELL SPAIN, S.A.",
    30123: "TESA TAPE, S.A.",
    70002: "UNO A ENE BREIXEN, S.L.",
    30558: "LURBE GRUP, S.A. (NGS-MONRAY)",
    31042: "AS COMPUTER MACCENTER, S.L.",
    30580: "AIRONFIX",
    70000: "TECHDATA ESPAÑA, S.L.",
    31319: "COMUNICACIONES LAGO, S.L. (BEEP SANTIAG)",
    31356: "NIEFENVER IBERICA, S.L.",
    31359: "ELCOM SANTIAGO, S.L.L.",
    31349: "PLICO PRODUCTS, S.L.",
    31297: "MARCOS CASTRO VAZQUEZ",
    31302: "ABACO IMPORT, S.L.U.",
    31333: "NEWELL SPAIN, S.L.",
    31310: "ALCAMPO, S.A.",
    31342: "DISMARK PRODUCTS, S.L.",
    31337: "PLASTICOS PARDO, S.L.",
    31315: "NOVOCEL FLEXIBLES, S.L.",
    31353: "CASH GALICIA",
    31274: "HP PRINTING AND COMPUTING SOLUTIONS, S.L",
    31253: "CENEFAS Y COMPLEMENTOS, S.L.",
    31221: "PEGADAS, S. COOP. GALEGA",
    31244: "SUMINISTROS DE BEBIDAS ANDOFRAN, S.L.",
    31256: "ESCALA PAPELERIA TECNICA, S.A.",
    31248: "INDUSTRIAS TAGAR, S.A.",
    31453: "CAMPUS IBERICA, S.L.",
    31428: "ANTALIS IBERIA, S.A.",
    31461: "AMBAR PASSION, S.A.",
    31463: "HSM TECN.OFIC. Y MEDIO AMBIENTE ESPAÑA",
    31448: "AMAZON EU SARL SUCURSAL EN ESPAÑA",
    31591: "CARTONAJES PEREZ, S.L.",
    31499: "ANTONIO PAZOS S.A. (ANPASA - SUMELEC)",
    31481: "COMERCIAL DEL SUR DE PAPELERIA, S.L.",
    31490: "CASA VIGAR, S.L.",
    31475: "AUXIEMBAL, S.L.",
    31469: "DHP COMERPA S.L.U.",
    31489: "JIM SPORTS TECHNOLOGY S.L.",
    31590: "MINILAND S.A.",
    31495: "DISET, S.A.",
    31472: "SUPERCUT TOOLS, S.L. (WUTO)",
    31467: "TINO Y MARY",
    31496: "PIQUERAS Y CRESPO, S.L.",
    31483: "EXACLAIR, S.A.",
    31498: "DISTRIBUIDORA DOS S.A.",
    31497: "OFIAGUS, S.L. (PICKING PACK SANTIAGO)",
    31464: "DS SMITH PACKAGING CARTOGAL, S.A.U.",
    31480: "FILA IBERIA, S.L. (CANSON)",
    31465: "TALENS ESPAÑA, S.A.U.",
    31471: "MANIPULADOS LUHERMA, S.L.",
    31485: "REINER PLAY",
    31487: "MATERIAL EDUCATIVO HENBEA S.L.",
    31491: "TUNCALYA, S.L. (S.A.T. EL CASCO)",
    31482: "AVERY TICO, S.R.L.",
    31478: "INTERMARK - PACKAGING & LABELLING S.L.",
    31509: "DISTRIBUIDORA UNIVERSAL S.L. (INSTANT)",
    31506: "MAQUINSAN D.C., S.L.",
    31505: "BINNEY & SMITH EUROPE LTD. (CRAYOLA)",
    31504: "SAFESCAN B.V.",
    39002: "GESTION EDITORIAL BOYACA, S.L.",
    31510: "RICARSAT, S.L.",
    31514: "DOS OFFICE GROUP, S.L.",
    31511: "BRICOMART",
    31652: "CIESPACK, S.L.",
    31653: "GROOVY MOBILE SPAIN, S.L.",
    31655: "PAPELES Y DESARROLLOS, S.L. (PAYDES)",
    31641: "CENTRUM EUROPA",
    31634: "CILINDRO ESPACIO, S.L.",
    31632: "CSG S.A.",
    31682: "STEINBEIS PAPIER GMBH",
    10001: "DISTRISANTIAGO PAPELERIA, S.L.",
    31680: "DURABLE-HUNKE & JOCHHEIM GMBH & CO. KG",
    31672: "INCALL, S.P.A. (MITAMA)",
    31665: "MEDIA MARKT-SATURN, S.A.U.",
    31681: "UTANPLAS, S.L. (ARCHIVO 2000)",
    31661: "VIVALLOONS, S.L.",
    90001: "PHARMIA LDA.",
    90002: "PHARMIA LDA. (ORIGINAL BOTANIC)",
    31684: "JB COMERCIO GLOBAL, LDA.",
    31685: "EXACLAIR, S.A. (PRO NAPPE)",
    31657: "FORLETTER S.A. (UNICEF)",
    31668: "MOOVING PAPER EU S.L.",
    31667: "CARRERAS EUROEMBALAJE (METO SPAIN)",
    31686: "UO ESTUDIO S.L.",
    31676: "KL-1 MOBILIARIO DE OFICINA, S.L.",
    31683: "TAP PAINT FACTORY, S.L. (LA PAJARITA)",
    31669: "PC COMPONENTES Y MULTIMEDIA, S.L.U.",
    31679: "NEWELL BRANDS IBERIA, S.L.",
    31673: "DEPAU SISTEMAS, S.L.",
    31697: "HONG KONG SHANG TENG FURNITURE CO. LIMIT",
    31690: "HILOS Y CUERDAS DEL SEGURA, S.L.",
    31687: "BADOLATO MARTIN, CRISTINA (ALILO-ORITA)",
    31693: "BAIER SCHNEIDER GMBH&CO. KG (BRUNNEN)",
    90028: "JOMA SPORT, S.A.",
    90029: "U GROUP, S.R.L. (U-POWER)",
    90030: "INDUSTRIAL WEAR PAYPER, S.L.U.",
    90031: "SANTEX 2000 INTERNACIONAL, S.L.",
    90021: "TEXTIL REYTEX, S.L. (TEXTIL-R)",
    90022: "ADVERSIA, S.L.",
    90000: "DSG PLUS, S.A.",
    31696: "EZEDICHI, S.L.",
    90020: "INDUSTRIAL STARTER ESPAÑA, S.L.U.",
    90033: "MKTO CATAL IMPORTACIONES, S.L. (MAKITO)",
    90034: "SAVELO, S.L.",
    31695: "ARTEXO DECORACION, S.L.",
    31692: "INSIGHT HUNTERS, S.L. (INOXCROM)",
    31694: "MADE DESIGN 1967 S.L. (PLANNING SISPLAMO)",
    90016: "CONFECCIONES MAYTON, S.L.U. (WORK TEAM)",
    90017: "PORCELANA DE SARGADELOS, S.L.",
    90039: "TEXTILES Y BORDADOS LUA, S.L.",
    90040: "GRUPO VAL OPTICAL, S.L.",
    31688: "GAMELINE GMBH",
    90024: "VALENTO TEXTILE, S.L.",
    90023: "JIM SPORTS TECHNOLOGY S.L. (DSG PLUS)",
    90025: "TOMAS BODERO, S.A.",
    90026: "PRODUCTOS CLIMAX, S.A.",
    90027: "FICOESA, S.L. (WORKO)",
    90035: "CONFECCIONES TRIVI, S.L.",
    90036: "BLANKS DESIGN PROJETS, S.L.",
    90038: "ARIARCA, S.L. (CALCETINES GF)",
    90037: "CODEOR, S.L.",
    31689: "AMAZON BUSINESS EU SARL SUCURSAL EN ESPAÑA",
    90018: "NEW WAVE SPORTSWEAR, S.A.",
    90019: "FAL CALZADOS DE SEGURIDAD, S.A.",
    31691: "NAVIGATOR (AMOOS - TISSUE)",
    90003: "AENOR CONOCIMIENTO, S.L.U.",
    90005: "C.I.F.R.A., S.L.",
    90004: "UNIFORMES GARY'S, S.L.U.",
    90006: "JHK TRADER, S.L.",
    90007: "PARSAN GRAFICA, S. L.",
    90008: "VELILLA GROUP EUROPE, S.L.U.",
    90009: "FALK&ROSS GROUP SPAIN, S.L.U.",
    90010: "DISTRIBUIDORA TEXTIL TOPTEX SPAIN, S.L.",
    90011: "C D M SPORT, S. L.",
    90012: "FUNDI-TROF, S.L.",
    90013: "SOLO PARIS",
    90014: "GOR FACTORY, S.A. (ROLY - STAMINA)",
    90015: "MATA ESMORIS, CARMEN (XALLAS PUBLICIDAD)",
    90032: "SANCOSA, S.L.",
    90050: "BORDADOS ORDES, S.L. (AS PUNTADAS)",
    90051: "LOPEZ NOYA, MARIA ELENA",
    90041: "HELLY HANSEN SPORTWEAR, S.L.U.",
    90045: "FORLI SAFETY FOOTWEAR, S.L.",
    31702: "HONGKONG BAIBO INTER. TRADING CO LIMITED",
    90053: "CONFECCIONES ENCA, S.L.",
    90044: "TRAFIC MAT Y MAS, S.L.",
    31699: "HONGKONG BAIBO INTER. TRADING CO LIMITED",
    31700: "MCR INFO ELECTRONIC, S.L.",
    90048: "PLAÇA 18, S.L. (TEXTIL MALLORCA)",
    90046: "PROFARTIC, LDA.",
    90052: "ROSSINI 1969 S.P.A.",
    31698: "FELIX MARTINEZ DE LECEA SL (PIROTECNIA)",
    31701: "EMBAGAL, S.L.",
    31703: "J.G. PROFESSIONAL TOOLS (TODOTALADROS)",
    90042: "PORTWEST POLONIA",
    90043: "PORTWEST ESPAÑA",
}


# Función que maneja el proceso de registro de un nuevo proveedor, validando los datos proporcionados, creando el usuario y sus acompañantes en la base de datos,
# generando un token QR único, enviando un correo de confirmación, y mostrando mensajes de éxito o error según corresponda
def f_registro_proveedor():
    if current_user.is_authenticated:
        flash("Este usuario ya se encuentra registrado.", "warning")
        return redirect(url_for("router_proveedor.dashboard"))

    form = UsuarioProveedorForm()

    if form.validate_on_submit():

        nombres_ac   = request.form.getlist("acompanante_nombre")
        apellidos_ac = request.form.getlist("acompanante_apellido")
        cenas_ac     = request.form.getlist("acompanante_cena")

        if Usuario.query.filter_by(email=form.email.data).first():
            flash("El email ya está registrado.", "danger")
            return render_template("auth/registro_proveedor.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        username = createUsername(form.nombre.data, form.apellido1.data, form.apellido2.data)

        if Usuario.query.filter_by(nombre_usuario=username).first():
            flash("El nombre de usuario ya existe.", "danger")
            return render_template("auth/registro_proveedor.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        if not comprobarContraseña(form.password.data, form.confirmar_password.data):
            return render_template("auth/registro_proveedor.html", form=form,
                                   CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
                                   SHORT_YEAR=inject_year()['SHORT_YEAR'])

        qr_token = uuid.uuid4().hex
        while Usuario.query.filter_by(qr_token=qr_token).first():
            qr_token = uuid.uuid4().hex

        new_user = Usuario(
            nombre         = form.nombre.data,
            apellido1      = form.apellido1.data,
            apellido2      = form.apellido2.data,
            nombre_usuario = username,
            email          = form.email.data,
            nombre_empresa = (form.nombre_empresa.data or "").strip() or None,
            cif_empresa    = (form.cif_empresa.data    or "").strip() or None,
            codigo         = (form.codigo.data         or "").strip() or None,
            rol            = "proveedor",
            qr_token       = qr_token,
            estado         = True,
            tipo_vc        = TipoVCEnum.C,
            asiste_cena    = form.asiste_cena.data
        )
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.flush()

            for i, (nombre_ac, apellido_ac) in enumerate(zip(nombres_ac, apellidos_ac)):
                nombre_ac   = nombre_ac.strip()
                apellido_ac = apellido_ac.strip()

                if not nombre_ac or not apellido_ac:
                    continue

                qr_token_ac = uuid.uuid4().hex
                while Acompanante.query.filter_by(qr_token=qr_token_ac).first():
                    qr_token_ac = uuid.uuid4().hex

                asiste_cena_ac = i < len(cenas_ac) and cenas_ac[i] == "1"

                db.session.add(Acompanante(
                    usuario_id  = new_user.id,
                    nombre      = nombre_ac,
                    apellido    = apellido_ac,
                    qr_token    = qr_token_ac,
                    asiste_cena = asiste_cena_ac,
                    pernocta    = False   
                ))

            db.session.commit()
            login_user(new_user)
            acompanantes_creados = Acompanante.query.filter_by(usuario_id=new_user.id).all()
            correo_confirmacion_registro(new_user, acompanantes_creados)
            flash("Usuario registrado correctamente.", "success")
            return redirect(url_for("router_index.home"))

        except Exception as e:
            db.session.rollback()
            flash("Error al registrar el usuario.", "danger")
            print(e)

    return render_template(
        "auth/registro_proveedor.html",
        form=form,
        proveedores=PROVEEDORES,
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
        SHORT_YEAR=inject_year()['SHORT_YEAR']
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE NEGOCIO
# ═══════════════════════════════════════════════════════════════════════════════


# Función que maneja la visualización del catálogo de productos del proveedor, permitiendo buscar por nombre o ID, paginar los resultados, 
# y mostrar el catálogo en formato HTML o JSON para diferentes usos
def f_listar_productos_propios():
    busqueda     = request.args.get('busqueda', '').strip()
    page         = request.args.get('page', 1, type=int)
    per_page     = request.args.get('per_page', 20, type=int)
    formato      = request.args.get('formato', '')

    # 👉 normalmente el proveedor es el usuario logueado
    proveedor_id = current_user.id  

    query = Producto.query.filter_by(proveedor_id=proveedor_id)

    if busqueda:
        query = query.filter(
            db.or_(
                Producto.nombre.ilike(f'%{busqueda}%'),
                db.cast(Producto.id, db.String).ilike(f'%{busqueda}%')
            )
        )

    paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
    has_more   = paginacion.has_next

    # JSON (para infinite scroll o AJAX)
    if formato == 'json':
        html = render_template(
            'partials/_cards_productos_comercial.html',
            productos=paginacion.items
        )
        return jsonify({
            'html':     html,
            'has_more': has_more,
            'total':    paginacion.total,
            'loaded':   page * per_page
        })

    # HTML normal
    return render_template(
        'proveedor/proveedor_catalogo.html',
        productos   = paginacion.items,
        busqueda    = busqueda,
        has_more    = has_more
    )



# Función que maneja la visualización del detalle de un producto específico del proveedor, validando que el producto exista y que el proveedor tenga permiso para verlo,
# y mostrando la información detallada del producto en el HTML
def f_detalle_producto(producto_id):

    producto = Producto.query.filter_by(id=producto_id).first()

    if not producto:
         flash("Producto no encontrado.", "danger")
         return redirect(url_for("router_comercial.catalogo"))
    
    if producto.proveedor_id != current_user.id:
         flash("No tienes permiso para ver este producto.", "danger")
         return redirect(url_for("router_comercial.catalogo"))

    return render_template("proveedor/proveedor_catalogo.html", producto=producto)



# Función que maneja la visualización del QR del proveedor, generando la imagen QR a partir del token del proveedor, 
# obteniendo los acompañantes asociados al proveedor y sus respectivos QR, y mostrando toda esta información en el HTML
def f_mi_qr_proveedor(proveedor_id):
    proveedor = Usuario.query.get(proveedor_id)

    if not proveedor or not proveedor.qr_token:
        flash("No tienes un QR asignado.", "warning")
        return redirect(url_for("router_proveedor.dashboard"))

    qr_base64 = generar_qr_imagen_64(proveedor.qr_token)

    acompanantes = Acompanante.query.filter_by(usuario_id=proveedor_id).all()
    acompanantes_qr = [
        {
            "nombre":    ac.nombre,
            "apellido":  ac.apellido,
            "qr_base64": generar_qr_imagen_64(ac.qr_token) if ac.qr_token else None
        }
        for ac in acompanantes
    ]

    return render_template(
        "proveedor/proveedor_qr.html",
        proveedor       = proveedor,
        qr_base64       = qr_base64,
        acompanantes_qr = acompanantes_qr,
        now             = datetime.now(),
        CURRENT_YEAR=inject_year()['CURRENT_YEAR'],
        SHORT_YEAR=inject_year()['SHORT_YEAR']
    )




# Función que maneja la visualización del mapa de stands, obteniendo los stands reservados y su información asociada, 
# verificando si el proveedor tiene una solicitud activa, y mostrando el mapa con los stands reservados y la información relevante para el proveedor
def f_mapa_stands():
    stands_reservados = Stand.query.filter(
        Stand.estado != EstadoStandEnum.disponible
    ).with_entities(Stand.numero_stand).all()

    numeros_reservados = [s.numero_stand for s in stands_reservados]

    tiene_solicitud_activa = Solicitud.query.filter(
        Solicitud.usuario_id == current_user.id,
        Solicitud.estado.in_(["ocupado", "pre_reservado", "asignado_por_admin","confirmada"])
    ).first() is not None

    return render_template(
        "proveedor/proveedor_mapa.html",
        stands_reservados=numeros_reservados,
        tiene_solicitud_activa=tiene_solicitud_activa,
        now=datetime.now()
    )
    
    

# Función que maneja la visualización de las solicitudes del proveedor, obteniendo las solicitudes asociadas al proveedor que no estén canceladas por el admin,
# cargando la información relacionada de stands, mobiliario, y extras, y mostrando esta información en el HTML para que el proveedor pueda revisar el estado de sus solicitudes
def f_mis_solicitudes(proveedor_id):
    solicitudes = (
        Solicitud.query
        .filter_by(usuario_id=proveedor_id)
        .filter(Solicitud.estado != "cancelada_admin")
        .options(joinedload(Solicitud.detalles_stand))
        .options(joinedload(Solicitud.detalles_mobiliario))
        .options(joinedload(Solicitud.extras))
        .order_by(Solicitud.fecha_solicitud.desc())
        .all()
    )
    config = Config.query.first()
    return render_template(
        "proveedor/proveedor_solicitudes.html",
        solicitudes=solicitudes,
        config=config,
        now=datetime.now()
    )



# Función que maneja la obtención del estado de los stands, obteniendo todos los stands y su información asociada, 
# incluyendo el proveedor que tiene cada stand reservado, y devolviendo esta información en formato JSON para ser utilizada 
# en la visualización del mapa de stands o en otras partes del sistema
def f_obtener_estado_stands():
    stands = Stand.query.all()
    resultado = {}

    for stand in stands:
        proveedor = ""
        if stand.solicitud and stand.solicitud.usuario and stand.solicitud.usuario.nombre_empresa:
            proveedor = stand.solicitud.usuario.nombre_empresa

        resultado[stand.numero_stand] = {
            "estado": stand.estado.value,
            "proveedor": proveedor,
            "solicitud_id": stand.solicitud_id,
            "precio": float(stand.precio),
            "dimensiones": float(stand.dimensiones) if stand.dimensiones else 9
        }

    return jsonify(resultado)



# Función que maneja la confirmación de una solicitud de stands por parte del proveedor, validando que el proveedor no tenga ya una solicitud confirmada,
# verificando que los stands seleccionados estén disponibles, creando o actualizando la solicitud del proveedor, 
# actualizando el estado de los stands seleccionados a pre-reservado, registrando el historial de cambios de estado de los stands, 
# y devolviendo la información de la solicitud confirmada y el total a pagar por el proveedor
def f_confirmar_pedido():
    data = request.get_json()
    stands_numeros = data.get("stands", [])

    solicitud_confirmada = Solicitud.query.filter(
        Solicitud.usuario_id == current_user.id,
        Solicitud.estado == "confirmada",
        Solicitud.detalles_stand.any()
    ).first()

    if solicitud_confirmada:
        return jsonify({
            "ok": False,
            "error": "YA_TIENE_STANDS_CONFIRMADOS",
            "message": "No puedes solicitar más stands porque ya tienes una solicitud confirmada."
        }), 403

    if not stands_numeros:
        return jsonify({"error": "No hay stands seleccionados"}), 400

    solicitud = Solicitud.query.filter_by(
        usuario_id=current_user.id,
        estado="pre_reservado"
    ).first()

    if not solicitud:
        solicitud = Solicitud(
            usuario_id=current_user.id,
            observaciones=None,
            fecha_solicitud=datetime.now(),
            estado="pre_reservado"
        )
        db.session.add(solicitud)
        db.session.flush()
    else:
        db.session.flush()

    total = 0

    for numero_stand in stands_numeros:

        stand = Stand.query.filter_by(numero_stand=numero_stand).first()
        if not stand:
            continue

        if stand.estado != EstadoStandEnum.disponible:
            continue

        existente = DetalleSolicitudStand.query.filter_by(
            solicitud_id=solicitud.id,
            stand_id=stand.numero_stand
        ).first()

        if existente:
            continue

        # ─────────────────────────────
        # ESTADO ANTERIOR (IMPORTANTE)
        # ─────────────────────────────
        estado_anterior = stand.estado.value

        # ─────────────────────────────
        # DETALLE SOLICITUD
        # ─────────────────────────────
        detalle = DetalleSolicitudStand(
            solicitud_id=solicitud.id,
            stand_id=stand.numero_stand,
            cantidad=1,
            precio_total=stand.precio
        )

        db.session.add(detalle)

        # ─────────────────────────────
        # ACTUALIZACIÓN STAND
        # ─────────────────────────────
        stand.estado = EstadoStandEnum.pre_reservado
        stand.solicitud_id = solicitud.id

        # ─────────────────────────────
        # HISTORIAL (CORREGIDO)
        # ─────────────────────────────
        historial = HistorialStand(
            stand_id=stand.numero_stand,
            accion="pre_reserva",
            estado_anterior=estado_anterior,
            estado_nuevo=EstadoStandEnum.pre_reservado.value,
            solicitud_origen_id=None,
            solicitud_destino_id=solicitud.id,
            usuario_origen_id=current_user.id,
            usuario_destino_id=None,
            observacion="Reserva desde formulario proveedor",
            fecha=datetime.now()
        )

        db.session.add(historial)

        total += float(stand.precio)

    db.session.commit()

    return jsonify({
        "ok": True,
        "solicitud_id": solicitud.id,
        "total": total
    })



# Función que maneja la visualización del catálogo de mobiliario disponible para el proveedor, obteniendo la lista de mobiliario desde la base de datos 
# y mostrando esta información en el HTML
def f_catalogo_mobiliario():
    mobiliario = Mobiliario().query.all()
    return render_template("proveedor/catalogo_mobiliario.html", mobiliario=mobiliario)



# Función que maneja la obtención de la solicitud actual del proveedor, buscando una solicitud en estado borrador, 
# y devolviendo su información en formato JSON para ser utilizada en la interfaz de confirmación de mobiliario
def f_get_solicitud_actual():
    solicitud = Solicitud.query.filter_by(
        usuario_id=current_user.id,
        estado="borrador"
    ).first()

    if not solicitud:
        return jsonify({
            "ok": True,
            "solicitud_id": None,
            "items": [],
            "extras": []
        })

    items = [
        {
            "mobiliario_id": d.mobiliario_id,
            "cantidad": d.cantidad
        }
        for d in solicitud.detalles_mobiliario
    ]

    extras = [
        {
            "nombre": e.descripcion,
            "cantidad": e.cantidad,
        }
        for e in solicitud.extras
    ]

    return jsonify({
        "ok": True,
        "solicitud_id": solicitud.id,
        "items": items,
        "extras": extras
    })   
    


# Función que maneja la confirmación de la solicitud de mobiliario por parte del proveedor, recibiendo los datos de mobiliario y extras desde el frontend,
# actualizando la solicitud en la base de datos, ajustando el stock del mobiliario, recalculando el precio total de la solicitud,
def _recalcular_total(solicitud):
    solicitud_stand = Solicitud.query.filter(
        Solicitud.usuario_id == solicitud.usuario_id,
        Solicitud.estado.in_(["confirmada", "asignado_por_admin", ""]),
        Solicitud.id != solicitud.id
    ).first()

    total_stands = 0
    if solicitud_stand:
        total_stands = db.session.query(
            db.func.coalesce(db.func.sum(DetalleSolicitudStand.precio_total), 0)
        ).filter_by(solicitud_id=solicitud_stand.id).scalar()

    total_mob = db.session.query(
        db.func.coalesce(db.func.sum(DetalleSolicitudMobiliario.precio_total), 0)
    ).filter_by(solicitud_id=solicitud.id).scalar()

    total_ext = db.session.query(
        db.func.coalesce(db.func.sum(Extra.precio * Extra.cantidad), 0)
    ).filter_by(solicitud_id=solicitud.id).scalar()

    solicitud_db = Solicitud.query.filter_by(id=solicitud.id).first()
    descuento = solicitud_db.descuento if solicitud_db else 0.0

    total_final = (float(total_mob) + float(total_ext) + float(total_stands)) - float(descuento)

    solicitud.precio_final = total_final
    if solicitud_stand:
        solicitud_stand.precio_final = total_final


# Función que maneja la confirmación de la solicitud de mobiliario por parte del proveedor, recibiendo los datos de mobiliario y extras desde el frontend,
# actualizando la solicitud en la base de datos, ajustando el stock del mobiliario, recalculando el precio total de la solicitud, 
# y devolviendo la información actualizada
def f_confirmar_mobiliario():
    data = request.get_json() or {}
    items = data.get("items", [])
    extras_data = data.get("extras", [])

    try:
        solicitud = Solicitud.query.filter_by(
            usuario_id=current_user.id,
            estado="borrador",
        ).first()

        if not solicitud:
            solicitud = Solicitud(
                usuario_id=current_user.id,
                estado="borrador"
            )
            db.session.add(solicitud)
            db.session.flush()

        old_items = DetalleSolicitudMobiliario.query.filter_by(
            solicitud_id=solicitud.id
        ).all()

        for item in old_items:
            mobiliario = Mobiliario.query.get(item.mobiliario_id)
            if mobiliario:
                mobiliario.stock += item.cantidad

        DetalleSolicitudMobiliario.query.filter_by(
            solicitud_id=solicitud.id
        ).delete(synchronize_session=False)

        db.session.flush()

        if not items and not extras_data:
            Extra.query.filter_by(solicitud_id=solicitud.id).delete(synchronize_session=False)
            solicitud.precio_final = 0.0
            db.session.commit()
            return jsonify({
                "ok": True,
                "solicitud_id": solicitud.id,
                "empty": True
            })

        for item in items:
            mobiliario_id = item.get("mobiliario_id")
            cantidad = int(item.get("cantidad", 1))

            mobiliario = Mobiliario.query.with_for_update().get(mobiliario_id)

            if not mobiliario:
                db.session.rollback()
                return jsonify({"ok": False, "error": "NO_EXISTE"}), 404

            if mobiliario.stock < cantidad:
                db.session.rollback()
                return jsonify({"ok": False, "error": "STOCK_INSUFICIENTE"}), 400

            mobiliario.stock -= cantidad

            db.session.add(DetalleSolicitudMobiliario(
                solicitud_id=solicitud.id,
                mobiliario_id=mobiliario_id,
                cantidad=cantidad,
                precio_total=float(mobiliario.precio) * cantidad
            ))

        extras_existentes = {e.descripcion: e for e in solicitud.extras}
        extras_recibidos = set()

        for extra in extras_data:
            descripcion = (extra.get("nombre") or "").strip()
            cantidad = int(extra.get("cantidad", 1))

            if not descripcion:
                continue

            extras_recibidos.add(descripcion)
            extra_db = extras_existentes.get(descripcion)

            if extra_db:
                extra_db.cantidad = cantidad
                if "precio" in extra and extra["precio"] is not None:
                    extra_db.precio = float(extra["precio"])
            else:
                db.session.add(Extra(
                    solicitud_id=solicitud.id,
                    descripcion=descripcion,
                    cantidad=cantidad,
                    precio=float(extra.get("precio") or 0)
                ))

        for desc, extra_db in extras_existentes.items():
            if desc not in extras_recibidos:
                db.session.delete(extra_db)

        db.session.flush()
        _recalcular_total(solicitud)
        db.session.commit()

        return jsonify({
            "ok": True,
            "solicitud_id": solicitud.id,
            "precio_final": solicitud.precio_final
        })

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"ok": False, "error": "ERROR_INTERNO"}), 500
