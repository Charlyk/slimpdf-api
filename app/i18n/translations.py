"""Translation system for SlimPDF API."""

from contextvars import ContextVar
from typing import Literal

from app.i18n.messages import Messages

# Supported languages
SupportedLanguage = Literal["en", "es", "fr", "de", "pt", "it", "ja", "zh", "ko"]

# Default language
DEFAULT_LANGUAGE: SupportedLanguage = "en"

# Context variable for current language (thread-safe)
current_language: ContextVar[SupportedLanguage] = ContextVar(
    "current_language", default=DEFAULT_LANGUAGE
)

# Translation dictionaries by language
TRANSLATIONS: dict[SupportedLanguage, dict[str, str]] = {
    "en": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "File size {actual_size_mb:.1f}MB exceeds limit of {max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "Expected {expected} file, got {actual}",
        Messages.FILE_COUNT_EXCEEDED: "Too many files ({actual_count}). Maximum allowed: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Daily limit of {limit} {tool} operations reached. Upgrade to Pro for unlimited access.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Authentication required",
        Messages.AUTH_INVALID_TOKEN: "Invalid token: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "Token has expired",
        Messages.AUTH_INVALID_USER_ID: "Invalid user ID in token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Use API key authentication endpoint",
        Messages.AUTH_PRO_REQUIRED: "Pro subscription required for this feature",
        # API key errors
        Messages.API_KEY_INVALID: "Invalid or revoked API key",
        Messages.API_KEY_REVOKED: "API key has been revoked",
        Messages.API_KEY_REQUIRED: "API key required",
        Messages.API_KEY_INVALID_FORMAT: "Invalid API key format. Expected sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "API key user not found",
        Messages.API_KEY_PRO_REQUIRED: "API access requires Pro subscription",
        Messages.API_KEY_MAX_LIMIT: "Maximum of {max_keys} active API keys allowed",
        Messages.API_KEY_STORE_WARNING: "Store this key securely - it cannot be retrieved again!",
        Messages.API_KEY_NOT_FOUND: "API key not found or already revoked",
        Messages.API_KEY_REVOKED_SUCCESS: "API key revoked successfully",
        Messages.API_KEY_INVALID_ID: "Invalid key ID",
        # Job errors
        Messages.JOB_NOT_FOUND: "Job {job_id} not found",
        Messages.JOB_EXPIRED: "Download link for job {job_id} has expired",
        Messages.JOB_PENDING: "Job is still pending. Please wait.",
        Messages.JOB_PROCESSING: "Job is still processing. Please wait.",
        Messages.JOB_FAILED: "Job failed: {error}",
        Messages.JOB_FILE_NOT_FOUND: "Output file not found",
        # Success messages
        Messages.COMPRESS_STARTED: "File uploaded. Processing started.",
        Messages.MERGE_STARTED: "Files uploaded. Merge processing started.",
        Messages.IMAGE_TO_PDF_STARTED: "Images uploaded. Conversion started.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "You already have a Pro subscription",
        Messages.BILLING_USER_NOT_FOUND: "User not found",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Stripe prices not configured",
        Messages.BILLING_NO_ACCOUNT: "No billing account found",
        Messages.BILLING_MISSING_SIGNATURE: "Missing Stripe signature",
        Messages.BILLING_INVALID_SIGNATURE: "Invalid signature",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Forbidden: Invalid or missing Origin header",
    },
    "es": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "El archivo de {actual_size_mb:.1f}MB excede el limite de {max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "Se esperaba un archivo {expected}, se recibio {actual}",
        Messages.FILE_COUNT_EXCEEDED: "Demasiados archivos ({actual_count}). Maximo permitido: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Limite diario de {limit} operaciones de {tool} alcanzado. Actualiza a Pro para acceso ilimitado.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Autenticacion requerida",
        Messages.AUTH_INVALID_TOKEN: "Token invalido: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "El token ha expirado",
        Messages.AUTH_INVALID_USER_ID: "ID de usuario invalido en el token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Usa el endpoint de autenticacion con API key",
        Messages.AUTH_PRO_REQUIRED: "Se requiere suscripcion Pro para esta funcion",
        # API key errors
        Messages.API_KEY_INVALID: "API key invalida o revocada",
        Messages.API_KEY_REVOKED: "La API key ha sido revocada",
        Messages.API_KEY_REQUIRED: "API key requerida",
        Messages.API_KEY_INVALID_FORMAT: "Formato de API key invalido. Se esperaba sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "Usuario de API key no encontrado",
        Messages.API_KEY_PRO_REQUIRED: "El acceso API requiere suscripcion Pro",
        Messages.API_KEY_MAX_LIMIT: "Maximo de {max_keys} API keys activas permitidas",
        Messages.API_KEY_STORE_WARNING: "Guarda esta clave de forma segura - no se puede recuperar despues!",
        Messages.API_KEY_NOT_FOUND: "API key no encontrada o ya revocada",
        Messages.API_KEY_REVOKED_SUCCESS: "API key revocada exitosamente",
        Messages.API_KEY_INVALID_ID: "ID de clave invalido",
        # Job errors
        Messages.JOB_NOT_FOUND: "Trabajo {job_id} no encontrado",
        Messages.JOB_EXPIRED: "El enlace de descarga para el trabajo {job_id} ha expirado",
        Messages.JOB_PENDING: "El trabajo esta pendiente. Por favor espera.",
        Messages.JOB_PROCESSING: "El trabajo se esta procesando. Por favor espera.",
        Messages.JOB_FAILED: "El trabajo fallo: {error}",
        Messages.JOB_FILE_NOT_FOUND: "Archivo de salida no encontrado",
        # Success messages
        Messages.COMPRESS_STARTED: "Archivo subido. Procesamiento iniciado.",
        Messages.MERGE_STARTED: "Archivos subidos. Fusion iniciada.",
        Messages.IMAGE_TO_PDF_STARTED: "Imagenes subidas. Conversion iniciada.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "Ya tienes una suscripcion Pro",
        Messages.BILLING_USER_NOT_FOUND: "Usuario no encontrado",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Precios de Stripe no configurados",
        Messages.BILLING_NO_ACCOUNT: "No se encontro cuenta de facturacion",
        Messages.BILLING_MISSING_SIGNATURE: "Falta firma de Stripe",
        Messages.BILLING_INVALID_SIGNATURE: "Firma invalida",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Prohibido: Cabecera Origin invalida o faltante",
    },
    "fr": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "La taille du fichier {actual_size_mb:.1f}Mo depasse la limite de {max_size_mb}Mo",
        Messages.FILE_TYPE_INVALID: "Fichier {expected} attendu, {actual} recu",
        Messages.FILE_COUNT_EXCEEDED: "Trop de fichiers ({actual_count}). Maximum autorise: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Limite quotidienne de {limit} operations {tool} atteinte. Passez a Pro pour un acces illimite.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Authentification requise",
        Messages.AUTH_INVALID_TOKEN: "Token invalide: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "Le token a expire",
        Messages.AUTH_INVALID_USER_ID: "ID utilisateur invalide dans le token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Utilisez le point d'acces d'authentification par cle API",
        Messages.AUTH_PRO_REQUIRED: "Abonnement Pro requis pour cette fonctionnalite",
        # API key errors
        Messages.API_KEY_INVALID: "Cle API invalide ou revoquee",
        Messages.API_KEY_REVOKED: "La cle API a ete revoquee",
        Messages.API_KEY_REQUIRED: "Cle API requise",
        Messages.API_KEY_INVALID_FORMAT: "Format de cle API invalide. Attendu sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "Utilisateur de la cle API non trouve",
        Messages.API_KEY_PRO_REQUIRED: "L'acces API necessite un abonnement Pro",
        Messages.API_KEY_MAX_LIMIT: "Maximum de {max_keys} cles API actives autorisees",
        Messages.API_KEY_STORE_WARNING: "Conservez cette cle en securite - elle ne peut pas etre recuperee!",
        Messages.API_KEY_NOT_FOUND: "Cle API non trouvee ou deja revoquee",
        Messages.API_KEY_REVOKED_SUCCESS: "Cle API revoquee avec succes",
        Messages.API_KEY_INVALID_ID: "ID de cle invalide",
        # Job errors
        Messages.JOB_NOT_FOUND: "Tache {job_id} non trouvee",
        Messages.JOB_EXPIRED: "Le lien de telechargement pour la tache {job_id} a expire",
        Messages.JOB_PENDING: "La tache est en attente. Veuillez patienter.",
        Messages.JOB_PROCESSING: "La tache est en cours de traitement. Veuillez patienter.",
        Messages.JOB_FAILED: "La tache a echoue: {error}",
        Messages.JOB_FILE_NOT_FOUND: "Fichier de sortie non trouve",
        # Success messages
        Messages.COMPRESS_STARTED: "Fichier telecharge. Traitement demarre.",
        Messages.MERGE_STARTED: "Fichiers telecharges. Fusion demarree.",
        Messages.IMAGE_TO_PDF_STARTED: "Images telechargees. Conversion demarree.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "Vous avez deja un abonnement Pro",
        Messages.BILLING_USER_NOT_FOUND: "Utilisateur non trouve",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Prix Stripe non configures",
        Messages.BILLING_NO_ACCOUNT: "Aucun compte de facturation trouve",
        Messages.BILLING_MISSING_SIGNATURE: "Signature Stripe manquante",
        Messages.BILLING_INVALID_SIGNATURE: "Signature invalide",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Interdit: En-tete Origin invalide ou manquant",
    },
    "de": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "Dateigrosse {actual_size_mb:.1f}MB uberschreitet das Limit von {max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "{expected}-Datei erwartet, {actual} erhalten",
        Messages.FILE_COUNT_EXCEEDED: "Zu viele Dateien ({actual_count}). Maximum erlaubt: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Tagliches Limit von {limit} {tool}-Operationen erreicht. Upgrade auf Pro fur unbegrenzten Zugang.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Authentifizierung erforderlich",
        Messages.AUTH_INVALID_TOKEN: "Ungultiges Token: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "Token ist abgelaufen",
        Messages.AUTH_INVALID_USER_ID: "Ungultige Benutzer-ID im Token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Verwenden Sie den API-Schlussel-Authentifizierungsendpunkt",
        Messages.AUTH_PRO_REQUIRED: "Pro-Abonnement fur diese Funktion erforderlich",
        # API key errors
        Messages.API_KEY_INVALID: "Ungultiger oder widerrufener API-Schlussel",
        Messages.API_KEY_REVOKED: "API-Schlussel wurde widerrufen",
        Messages.API_KEY_REQUIRED: "API-Schlussel erforderlich",
        Messages.API_KEY_INVALID_FORMAT: "Ungultiges API-Schlussel-Format. Erwartet sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "API-Schlussel-Benutzer nicht gefunden",
        Messages.API_KEY_PRO_REQUIRED: "API-Zugang erfordert Pro-Abonnement",
        Messages.API_KEY_MAX_LIMIT: "Maximal {max_keys} aktive API-Schlussel erlaubt",
        Messages.API_KEY_STORE_WARNING: "Bewahren Sie diesen Schlussel sicher auf - er kann nicht wiederhergestellt werden!",
        Messages.API_KEY_NOT_FOUND: "API-Schlussel nicht gefunden oder bereits widerrufen",
        Messages.API_KEY_REVOKED_SUCCESS: "API-Schlussel erfolgreich widerrufen",
        Messages.API_KEY_INVALID_ID: "Ungultige Schlussel-ID",
        # Job errors
        Messages.JOB_NOT_FOUND: "Auftrag {job_id} nicht gefunden",
        Messages.JOB_EXPIRED: "Download-Link fur Auftrag {job_id} ist abgelaufen",
        Messages.JOB_PENDING: "Auftrag wartet noch. Bitte warten.",
        Messages.JOB_PROCESSING: "Auftrag wird noch verarbeitet. Bitte warten.",
        Messages.JOB_FAILED: "Auftrag fehlgeschlagen: {error}",
        Messages.JOB_FILE_NOT_FOUND: "Ausgabedatei nicht gefunden",
        # Success messages
        Messages.COMPRESS_STARTED: "Datei hochgeladen. Verarbeitung gestartet.",
        Messages.MERGE_STARTED: "Dateien hochgeladen. Zusammenfuhrung gestartet.",
        Messages.IMAGE_TO_PDF_STARTED: "Bilder hochgeladen. Konvertierung gestartet.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "Sie haben bereits ein Pro-Abonnement",
        Messages.BILLING_USER_NOT_FOUND: "Benutzer nicht gefunden",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Stripe-Preise nicht konfiguriert",
        Messages.BILLING_NO_ACCOUNT: "Kein Rechnungskonto gefunden",
        Messages.BILLING_MISSING_SIGNATURE: "Fehlende Stripe-Signatur",
        Messages.BILLING_INVALID_SIGNATURE: "Ungultige Signatur",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Verboten: Ungultiger oder fehlender Origin-Header",
    },
    "pt": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "Tamanho do arquivo {actual_size_mb:.1f}MB excede o limite de {max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "Esperado arquivo {expected}, recebido {actual}",
        Messages.FILE_COUNT_EXCEEDED: "Muitos arquivos ({actual_count}). Maximo permitido: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Limite diario de {limit} operacoes de {tool} atingido. Atualize para Pro para acesso ilimitado.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Autenticacao necessaria",
        Messages.AUTH_INVALID_TOKEN: "Token invalido: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "Token expirou",
        Messages.AUTH_INVALID_USER_ID: "ID de usuario invalido no token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Use o endpoint de autenticacao por chave API",
        Messages.AUTH_PRO_REQUIRED: "Assinatura Pro necessaria para este recurso",
        # API key errors
        Messages.API_KEY_INVALID: "Chave API invalida ou revogada",
        Messages.API_KEY_REVOKED: "Chave API foi revogada",
        Messages.API_KEY_REQUIRED: "Chave API necessaria",
        Messages.API_KEY_INVALID_FORMAT: "Formato de chave API invalido. Esperado sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "Usuario da chave API nao encontrado",
        Messages.API_KEY_PRO_REQUIRED: "Acesso API requer assinatura Pro",
        Messages.API_KEY_MAX_LIMIT: "Maximo de {max_keys} chaves API ativas permitidas",
        Messages.API_KEY_STORE_WARNING: "Guarde esta chave com seguranca - ela nao pode ser recuperada!",
        Messages.API_KEY_NOT_FOUND: "Chave API nao encontrada ou ja revogada",
        Messages.API_KEY_REVOKED_SUCCESS: "Chave API revogada com sucesso",
        Messages.API_KEY_INVALID_ID: "ID de chave invalido",
        # Job errors
        Messages.JOB_NOT_FOUND: "Trabalho {job_id} nao encontrado",
        Messages.JOB_EXPIRED: "Link de download para trabalho {job_id} expirou",
        Messages.JOB_PENDING: "Trabalho ainda pendente. Por favor aguarde.",
        Messages.JOB_PROCESSING: "Trabalho ainda em processamento. Por favor aguarde.",
        Messages.JOB_FAILED: "Trabalho falhou: {error}",
        Messages.JOB_FILE_NOT_FOUND: "Arquivo de saida nao encontrado",
        # Success messages
        Messages.COMPRESS_STARTED: "Arquivo enviado. Processamento iniciado.",
        Messages.MERGE_STARTED: "Arquivos enviados. Mesclagem iniciada.",
        Messages.IMAGE_TO_PDF_STARTED: "Imagens enviadas. Conversao iniciada.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "Voce ja tem uma assinatura Pro",
        Messages.BILLING_USER_NOT_FOUND: "Usuario nao encontrado",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Precos do Stripe nao configurados",
        Messages.BILLING_NO_ACCOUNT: "Nenhuma conta de cobranca encontrada",
        Messages.BILLING_MISSING_SIGNATURE: "Assinatura Stripe ausente",
        Messages.BILLING_INVALID_SIGNATURE: "Assinatura invalida",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Proibido: Cabecalho Origin invalido ou ausente",
    },
    "it": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "Dimensione file {actual_size_mb:.1f}MB supera il limite di {max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "Atteso file {expected}, ricevuto {actual}",
        Messages.FILE_COUNT_EXCEEDED: "Troppi file ({actual_count}). Massimo consentito: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "Limite giornaliero di {limit} operazioni {tool} raggiunto. Passa a Pro per accesso illimitato.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "Autenticazione richiesta",
        Messages.AUTH_INVALID_TOKEN: "Token non valido: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "Token scaduto",
        Messages.AUTH_INVALID_USER_ID: "ID utente non valido nel token",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "Usa l'endpoint di autenticazione con chiave API",
        Messages.AUTH_PRO_REQUIRED: "Abbonamento Pro richiesto per questa funzionalita",
        # API key errors
        Messages.API_KEY_INVALID: "Chiave API non valida o revocata",
        Messages.API_KEY_REVOKED: "La chiave API e stata revocata",
        Messages.API_KEY_REQUIRED: "Chiave API richiesta",
        Messages.API_KEY_INVALID_FORMAT: "Formato chiave API non valido. Atteso sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "Utente chiave API non trovato",
        Messages.API_KEY_PRO_REQUIRED: "L'accesso API richiede abbonamento Pro",
        Messages.API_KEY_MAX_LIMIT: "Massimo {max_keys} chiavi API attive consentite",
        Messages.API_KEY_STORE_WARNING: "Conserva questa chiave in modo sicuro - non puo essere recuperata!",
        Messages.API_KEY_NOT_FOUND: "Chiave API non trovata o gia revocata",
        Messages.API_KEY_REVOKED_SUCCESS: "Chiave API revocata con successo",
        Messages.API_KEY_INVALID_ID: "ID chiave non valido",
        # Job errors
        Messages.JOB_NOT_FOUND: "Lavoro {job_id} non trovato",
        Messages.JOB_EXPIRED: "Link di download per lavoro {job_id} scaduto",
        Messages.JOB_PENDING: "Lavoro ancora in attesa. Attendere prego.",
        Messages.JOB_PROCESSING: "Lavoro ancora in elaborazione. Attendere prego.",
        Messages.JOB_FAILED: "Lavoro fallito: {error}",
        Messages.JOB_FILE_NOT_FOUND: "File di output non trovato",
        # Success messages
        Messages.COMPRESS_STARTED: "File caricato. Elaborazione avviata.",
        Messages.MERGE_STARTED: "File caricati. Unione avviata.",
        Messages.IMAGE_TO_PDF_STARTED: "Immagini caricate. Conversione avviata.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "Hai gia un abbonamento Pro",
        Messages.BILLING_USER_NOT_FOUND: "Utente non trovato",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Prezzi Stripe non configurati",
        Messages.BILLING_NO_ACCOUNT: "Nessun account di fatturazione trovato",
        Messages.BILLING_MISSING_SIGNATURE: "Firma Stripe mancante",
        Messages.BILLING_INVALID_SIGNATURE: "Firma non valida",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "Vietato: Header Origin non valido o mancante",
    },
    "ja": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "ファイルサイズ{actual_size_mb:.1f}MBが上限{max_size_mb}MBを超えています",
        Messages.FILE_TYPE_INVALID: "{expected}ファイルが必要ですが、{actual}を受信しました",
        Messages.FILE_COUNT_EXCEEDED: "ファイル数が多すぎます({actual_count})。最大許可数: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "{tool}の1日の上限{limit}回に達しました。Proにアップグレードして無制限アクセスを。",
        # Authentication errors
        Messages.AUTH_REQUIRED: "認証が必要です",
        Messages.AUTH_INVALID_TOKEN: "無効なトークン: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "トークンの有効期限が切れています",
        Messages.AUTH_INVALID_USER_ID: "トークン内のユーザーIDが無効です",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "APIキー認証エンドポイントを使用してください",
        Messages.AUTH_PRO_REQUIRED: "この機能にはProサブスクリプションが必要です",
        # API key errors
        Messages.API_KEY_INVALID: "無効または取り消されたAPIキー",
        Messages.API_KEY_REVOKED: "APIキーは取り消されました",
        Messages.API_KEY_REQUIRED: "APIキーが必要です",
        Messages.API_KEY_INVALID_FORMAT: "無効なAPIキー形式。sk_live_...が必要です",
        Messages.API_KEY_USER_NOT_FOUND: "APIキーのユーザーが見つかりません",
        Messages.API_KEY_PRO_REQUIRED: "APIアクセスにはProサブスクリプションが必要です",
        Messages.API_KEY_MAX_LIMIT: "有効なAPIキーは最大{max_keys}個までです",
        Messages.API_KEY_STORE_WARNING: "このキーを安全に保管してください - 再取得はできません!",
        Messages.API_KEY_NOT_FOUND: "APIキーが見つからないか、既に取り消されています",
        Messages.API_KEY_REVOKED_SUCCESS: "APIキーが正常に取り消されました",
        Messages.API_KEY_INVALID_ID: "無効なキーID",
        # Job errors
        Messages.JOB_NOT_FOUND: "ジョブ {job_id} が見つかりません",
        Messages.JOB_EXPIRED: "ジョブ {job_id} のダウンロードリンクの有効期限が切れています",
        Messages.JOB_PENDING: "ジョブは保留中です。お待ちください。",
        Messages.JOB_PROCESSING: "ジョブは処理中です。お待ちください。",
        Messages.JOB_FAILED: "ジョブが失敗しました: {error}",
        Messages.JOB_FILE_NOT_FOUND: "出力ファイルが見つかりません",
        # Success messages
        Messages.COMPRESS_STARTED: "ファイルがアップロードされました。処理を開始しました。",
        Messages.MERGE_STARTED: "ファイルがアップロードされました。結合を開始しました。",
        Messages.IMAGE_TO_PDF_STARTED: "画像がアップロードされました。変換を開始しました。",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "既にProサブスクリプションをお持ちです",
        Messages.BILLING_USER_NOT_FOUND: "ユーザーが見つかりません",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Stripeの価格が設定されていません",
        Messages.BILLING_NO_ACCOUNT: "請求アカウントが見つかりません",
        Messages.BILLING_MISSING_SIGNATURE: "Stripe署名がありません",
        Messages.BILLING_INVALID_SIGNATURE: "無効な署名",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "禁止: 無効または不足しているOriginヘッダー",
    },
    "zh": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "文件大小{actual_size_mb:.1f}MB超过限制{max_size_mb}MB",
        Messages.FILE_TYPE_INVALID: "期望{expected}文件，收到{actual}",
        Messages.FILE_COUNT_EXCEEDED: "文件过多({actual_count})。最多允许: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "已达到每日{limit}次{tool}操作限制。升级到Pro获取无限访问。",
        # Authentication errors
        Messages.AUTH_REQUIRED: "需要身份验证",
        Messages.AUTH_INVALID_TOKEN: "无效的令牌: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "令牌已过期",
        Messages.AUTH_INVALID_USER_ID: "令牌中的用户ID无效",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "请使用API密钥认证端点",
        Messages.AUTH_PRO_REQUIRED: "此功能需要Pro订阅",
        # API key errors
        Messages.API_KEY_INVALID: "无效或已撤销的API密钥",
        Messages.API_KEY_REVOKED: "API密钥已被撤销",
        Messages.API_KEY_REQUIRED: "需要API密钥",
        Messages.API_KEY_INVALID_FORMAT: "无效的API密钥格式。应为sk_live_...",
        Messages.API_KEY_USER_NOT_FOUND: "未找到API密钥用户",
        Messages.API_KEY_PRO_REQUIRED: "API访问需要Pro订阅",
        Messages.API_KEY_MAX_LIMIT: "最多允许{max_keys}个活动API密钥",
        Messages.API_KEY_STORE_WARNING: "请安全保存此密钥 - 无法再次获取!",
        Messages.API_KEY_NOT_FOUND: "未找到API密钥或已被撤销",
        Messages.API_KEY_REVOKED_SUCCESS: "API密钥撤销成功",
        Messages.API_KEY_INVALID_ID: "无效的密钥ID",
        # Job errors
        Messages.JOB_NOT_FOUND: "未找到任务 {job_id}",
        Messages.JOB_EXPIRED: "任务 {job_id} 的下载链接已过期",
        Messages.JOB_PENDING: "任务仍在等待中。请稍候。",
        Messages.JOB_PROCESSING: "任务仍在处理中。请稍候。",
        Messages.JOB_FAILED: "任务失败: {error}",
        Messages.JOB_FILE_NOT_FOUND: "未找到输出文件",
        # Success messages
        Messages.COMPRESS_STARTED: "文件已上传。处理已开始。",
        Messages.MERGE_STARTED: "文件已上传。合并已开始。",
        Messages.IMAGE_TO_PDF_STARTED: "图片已上传。转换已开始。",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "您已经拥有Pro订阅",
        Messages.BILLING_USER_NOT_FOUND: "未找到用户",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Stripe价格未配置",
        Messages.BILLING_NO_ACCOUNT: "未找到账单账户",
        Messages.BILLING_MISSING_SIGNATURE: "缺少Stripe签名",
        Messages.BILLING_INVALID_SIGNATURE: "无效的签名",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "禁止: 无效或缺少Origin头",
    },
    "ko": {
        # File validation errors
        Messages.FILE_SIZE_EXCEEDED: "파일 크기 {actual_size_mb:.1f}MB가 제한 {max_size_mb}MB를 초과합니다",
        Messages.FILE_TYPE_INVALID: "{expected} 파일이 필요하지만 {actual}을(를) 받았습니다",
        Messages.FILE_COUNT_EXCEEDED: "파일이 너무 많습니다 ({actual_count}). 최대 허용: {max_count}",
        # Rate limiting
        Messages.RATE_LIMIT_EXCEEDED: "일일 {tool} 작업 한도 {limit}회에 도달했습니다. Pro로 업그레이드하여 무제한 액세스를 받으세요.",
        # Authentication errors
        Messages.AUTH_REQUIRED: "인증이 필요합니다",
        Messages.AUTH_INVALID_TOKEN: "유효하지 않은 토큰: {error}",
        Messages.AUTH_TOKEN_EXPIRED: "토큰이 만료되었습니다",
        Messages.AUTH_INVALID_USER_ID: "토큰의 사용자 ID가 유효하지 않습니다",
        Messages.AUTH_USE_API_KEY_ENDPOINT: "API 키 인증 엔드포인트를 사용하세요",
        Messages.AUTH_PRO_REQUIRED: "이 기능을 사용하려면 Pro 구독이 필요합니다",
        # API key errors
        Messages.API_KEY_INVALID: "유효하지 않거나 취소된 API 키",
        Messages.API_KEY_REVOKED: "API 키가 취소되었습니다",
        Messages.API_KEY_REQUIRED: "API 키가 필요합니다",
        Messages.API_KEY_INVALID_FORMAT: "유효하지 않은 API 키 형식. sk_live_...이어야 합니다",
        Messages.API_KEY_USER_NOT_FOUND: "API 키 사용자를 찾을 수 없습니다",
        Messages.API_KEY_PRO_REQUIRED: "API 액세스에는 Pro 구독이 필요합니다",
        Messages.API_KEY_MAX_LIMIT: "최대 {max_keys}개의 활성 API 키가 허용됩니다",
        Messages.API_KEY_STORE_WARNING: "이 키를 안전하게 보관하세요 - 다시 가져올 수 없습니다!",
        Messages.API_KEY_NOT_FOUND: "API 키를 찾을 수 없거나 이미 취소되었습니다",
        Messages.API_KEY_REVOKED_SUCCESS: "API 키가 성공적으로 취소되었습니다",
        Messages.API_KEY_INVALID_ID: "유효하지 않은 키 ID",
        # Job errors
        Messages.JOB_NOT_FOUND: "작업 {job_id}을(를) 찾을 수 없습니다",
        Messages.JOB_EXPIRED: "작업 {job_id}의 다운로드 링크가 만료되었습니다",
        Messages.JOB_PENDING: "작업이 아직 대기 중입니다. 잠시 기다려 주세요.",
        Messages.JOB_PROCESSING: "작업이 아직 처리 중입니다. 잠시 기다려 주세요.",
        Messages.JOB_FAILED: "작업 실패: {error}",
        Messages.JOB_FILE_NOT_FOUND: "출력 파일을 찾을 수 없습니다",
        # Success messages
        Messages.COMPRESS_STARTED: "파일이 업로드되었습니다. 처리가 시작되었습니다.",
        Messages.MERGE_STARTED: "파일이 업로드되었습니다. 병합이 시작되었습니다.",
        Messages.IMAGE_TO_PDF_STARTED: "이미지가 업로드되었습니다. 변환이 시작되었습니다.",
        # Billing errors
        Messages.BILLING_ALREADY_PRO: "이미 Pro 구독을 보유하고 있습니다",
        Messages.BILLING_USER_NOT_FOUND: "사용자를 찾을 수 없습니다",
        Messages.BILLING_STRIPE_NOT_CONFIGURED: "Stripe 가격이 구성되지 않았습니다",
        Messages.BILLING_NO_ACCOUNT: "청구 계정을 찾을 수 없습니다",
        Messages.BILLING_MISSING_SIGNATURE: "Stripe 서명이 없습니다",
        Messages.BILLING_INVALID_SIGNATURE: "유효하지 않은 서명",
        # Origin validation
        Messages.ORIGIN_FORBIDDEN: "금지됨: 유효하지 않거나 누락된 Origin 헤더",
    },
}


class Translator:
    """Translator class for getting localized messages."""

    def __init__(self, language: SupportedLanguage = DEFAULT_LANGUAGE):
        self.language = language
        self._translations = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])
        self._fallback = TRANSLATIONS[DEFAULT_LANGUAGE]

    def get(self, key: str, **kwargs) -> str:
        """
        Get a translated message by key with optional format arguments.

        Falls back to English if the key is not found in the current language.
        Falls back to the key itself if not found in any language.
        """
        template = self._translations.get(key) or self._fallback.get(key) or key

        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError:
                # If formatting fails, return template as-is
                return template

        return template

    def __call__(self, key: str, **kwargs) -> str:
        """Shorthand for get()."""
        return self.get(key, **kwargs)


def get_translator(language: str | None = None) -> Translator:
    """
    Get a translator for the specified language.

    If no language is specified, uses the current context language.
    If the language is not supported, falls back to English.
    """
    if language is None:
        language = current_language.get()

    # Normalize language code (e.g., "en-US" -> "en")
    if language and "-" in language:
        language = language.split("-")[0]

    # Validate language
    if language not in TRANSLATIONS:
        language = DEFAULT_LANGUAGE

    return Translator(language)


def set_language(language: SupportedLanguage) -> None:
    """Set the current language in the context."""
    current_language.set(language)


def get_language() -> SupportedLanguage:
    """Get the current language from the context."""
    return current_language.get()
