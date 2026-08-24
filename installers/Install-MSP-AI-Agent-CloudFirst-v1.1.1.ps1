<#
MSP AI Agent - Cloud First / Local Fallback v1.1.1
Installs or updates the project without committing/storing API secrets.

Default behavior:
- Overlay corrected source onto the target.
- Preserve an existing .env and runtime/knowledge data.
- Enforce strict cloud-first routing flags.
- Ollama is optional and is only the fallback provider.
#>

[CmdletBinding()]
param(
    [string]$TargetRoot = "C:\Projects\msp-local-ai-agent-fresh",
    [switch]$ForceReplace,
    [switch]$InstallPrereqs,
    [switch]$InstallLocalFallback
)

$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$Path){
    if(-not (Test-Path $Path)){
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Refresh-Path {
    $machine = [Environment]::GetEnvironmentVariable("Path","Machine")
    $user = [Environment]::GetEnvironmentVariable("Path","User")
    $env:Path = "$machine;$user"
}

function Find-Python {
    Refresh-Path
    $pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )
    if($pf86){
        $candidates += @("$pf86\Python312\python.exe","$pf86\Python311\python.exe")
    }
    foreach($candidate in $candidates){
        if($candidate -and (Test-Path $candidate)){ return $candidate }
    }
    try{
        $cmd = Get-Command python -ErrorAction Stop
        if($cmd.Source){ return $cmd.Source }
    }catch{}
    return $null
}

function Winget-Install([string]$Id,[string]$Name){
    if(-not (Get-Command winget -ErrorAction SilentlyContinue)){
        throw "winget is not available. Install $Name manually."
    }
    winget install --id $Id -e --accept-source-agreements --accept-package-agreements
    if($LASTEXITCODE -ne 0){
        throw "winget failed installing $Name ($Id)."
    }
    Refresh-Path
}

function Set-EnvValue([string]$File,[string]$Name,[string]$Value){
    $text = if(Test-Path $File){ Get-Content $File -Raw }else{ "" }
    $pattern = "(?m)^\s*$([regex]::Escape($Name))\s*=.*$"
    $replacement = "$Name=$Value"
    if($text -match $pattern){
        $text = [regex]::Replace($text,$pattern,$replacement)
    }else{
        $text += "`r`n$replacement`r`n"
    }
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($File,$text,$enc)
}

if($ForceReplace -and (Test-Path $TargetRoot)){
    Remove-Item $TargetRoot -Recurse -Force
}

Ensure-Dir $TargetRoot

$tempRoot = Join-Path $env:TEMP ("msp-ai-cloudfirst-" + [guid]::NewGuid().ToString("N"))
$tempZip = "$tempRoot.zip"
Ensure-Dir $tempRoot

$payload = @'
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≤»="25‡…ç,≠π©•ƒƒΩΩÈ%¡¥ƒ·Ω ¨‘≈Ω	-Õ9≠Yô…·ë—%QçeΩ±Ö›π≠Ÿ±EÕ0›=a≈›iº¿ÕH’—ô≈≠UŸIÕ≈µeÖaA9‹–…]Qç›A-ââ≈!I¡ù•1=È±ò…Ö≠Õï]ô¡‹‡·AAôYïYú‹ÕÈ»¡)’°]eDŸÿ—Â ≈‰‹Ω•U-5Ω≠¡Â≈%Ë›UI±1!ïàŸaµÈΩë≈Ÿ≠•ï‘—Ö¿—’i≈AÕµù!ΩhÂQΩ≈=ï)=]±·¡µ%ŸU]h—EÖ\¿ŸE≈MçÕM]—$…Eç<¿’µeÕË’ë\ÂÈ©)âÕ©MåΩPÿÂâ\Â]Ââê≠∏’ïÈµH¡A	©¡eå—aë9©a<·aŸ›ïú¿’›…πà¡Q—ë»≈d—e›≠,Õ1’Uù•!e!U°)!@ÿÂM1……‡·	¡·‰≈UQ≈Â›âëΩY’e,…≈	…I10Õ≠9	Pƒ›Ωa≠ÈŸçMàΩe∏≠≠ï`—µôi‘Ω’ô…âË≠—òº≈•–’Ÿ≈e∏¿›5—Y≈È±Ω±XŸ©†Ÿ5ΩïâDŸ…ÖçºÂπâ·‹»Â°	—ç±âH≈‘‘≈π10Ωô]…iÕŸÖQi%-ÖY≈0·‹≠(≈•)—±	âŸëe•iâï•©πÃ≈-\ŸQ°•π1!ïîŸEπH…%ÂA!ùU-4’à¡†Â–ÕA=<ÿ≠±)»≠¡Ö]TÂD¡—¡ÖÈπ—âL–Â¡—¡ëÈÿ¡±(ÿ—)•]·ùH»Õ‘¡≈]=•—!πQŸ<≠’¥…†ÕïY—º»≈<‡Ÿâ’≠]X—Y5µπ≈π—eY›e’¡)iŸ©≈9Ö,Â•ÿÃ≈%ôÖ°ï)ÂQÂeΩµ›Ω—ΩQ5±È±∞ÂUÕ·’eÂ¡8¡ùM≈5	ÑΩ¡i1,Ÿaa!Eπ–≈]	iµ%aI‰·U±)]—È≠…≠)—¡1Q’ŸeçIùç`‡ƒ…i-,¡ÖQX’≠±·Q)µ©ËŸDÕ8ÿ≠»—%∞Õ=‡–’µiπ-Â≠Ö!U°i±Ã¡ieô•ï°IQ¡¿Õ…U¡	X–ƒ’≈ŸYîÂ·ô°]i1ÂåΩ(—≈±ëA·h›-¨ΩAÂ¨ÂŸç—IïU›—©eÂ‘ÿ¡†ÂÖ1µπ…Ω!Ñ≈9Ωi=Â»Ã–ÕåΩ°)AÂUå’Q‡ºÂ¿·]±·°° ≠Qâ∏…¥––ÂhÕô<…ùÖ°ïedÕ≈°ôMeÂïÃÿÃ·•ï	Qƒ…≠©Iï		π!›]-ÖQ¡Õ±Ã—π±ù%i9AπY@–ƒ’Ö@ΩÑ‰‡Ÿ=’ÈY±eÕâ5ëâÈ›=Öç¿≈¡Â(›•¡ÈŸYùQ5P…•0¡Õ’∞≈µ9¡\≈0Â=I·ºÃŸ¡i1·=<›U11AŸÕå·…Ei ≠çaUô°Ö-5E]…!0—¡=@—©çÖ›…A±ù%îÃΩ’ï1‰ŸiŸô≠Ÿ…ïdÂ—Iå—EU±%Ö9MaDŸ	MŸ5Ωë°°)!Ω·’ŸhÕUç¡95i—•ÕU»—aQ‡≠åΩ-ËŸeÑÕ`—d·¥›’DÂÂL‹ÂÂ\ŸY@—ƒ≠‹’EM›5ù·eaï°›î›-E—	Èçµ5Ÿâa9›`…πi\‘¡0Õ9©çµ±›ëÂ›à…·¡dÕ≠’ç!≠±®›=‹¡EIA–··çº‰¡9I%eMEÕ1	•8Ÿµ§’Q··Q¡‡ÕÈê’ïÿŸï<≠°µI¨·ÈµŸ‘ΩÈi5‡Ω›Q§ºÂçë†ºÂ59PÂHƒÕîŸù°ë°Q	≠L≈Öùô≠1•’…)!e%ÕUE›¿≈ç%©¿¿Ÿ	T…π¡!M‹Õ’Uç≈5ç1ŸîŸI»‰Ω1§›º·›∏¡%›Q∞≠L‘≠≈I11Yµ≈…≈’≠0Â›d≠5YµŸµ›•π<º—59ei±â•—’—)°)§»ΩÑ…-Ñ¡•ï!1·(≈9L¡µ\Õ©·îŸΩŸE=©%YMç§’ÖEeΩ≈çô5πÂaµ1ï—ëîΩUÕ		E%	°Aƒ’i=EU›E-ÖåÕ)©0»≈ÈçÂ°h…Y’ë‰Õi])ôëÂŸâ!5’ç!µëY\≈ÿ…ÈeDΩ‘’ôEôQ°5±-Õπ`›e5ÕÕ·i›I)±≈Q9çEÖ%µ,…Y≠L≈-i©çΩŸçça]i-aiçU…	-@‰Ω1å·î’°…]]•≈)’âÖ—¡UM]--≠—%≠)%MÂÂQ›≠·≈¿≈%IL¡¡=©-¥¡Èµ%ù≠Ö…=]ô…a	—Ö-ç5»≠ï·YQ¡-º¡	i5Ω51(·Ω…iââÖ·X»≠	—âê‘≈Q∏Ÿ©¡1]ÕâŸ¥Ââ9Y≠5Ÿ¥≈≠Ëº¡P¡±’—ÈçUë9Â<’ÕùïÂÈπ4ŸEÕëΩŸUÑΩ--]›Y9ùùµ›≈]•A©!IQ’—I]AÂiΩeµ≈Ÿ1ë\›‹≈Y1h»Ω—9¡°©°…µ(ÃΩπ%eù…iE)=L¡ú·Âµ≠%°	Y≈’ŸM©ïUù≈òŸQ\¨‡¿≈°U≈›Må—IP·ùô	)§—›·	ΩU°®’§º—,‘‘≈›a—ëU5ÕAa%›aî‰Õ©•=‹≈·ç¨…eΩE]Ω›â=…QY(Õ%°›Ÿ•—UΩM°-ùeX··E%·µµiΩÕ≈î¿¡ç≈·§Ã¡Ω8ΩE%…•µ’	πÖYaA≈ÂïU≈aå‘·%U=)YŸ5±âA·9)•$–≈8Õ≠ÕÕ—\›Ÿ…¡5EUAQiEÈYçQAe!·≠È±È	QI5›)≠Eç±Y—MAú¡≠QÂ	’Qç‘Ÿâ≠•≈1ÿ—4ÂU,›»Ωù!1)å≈1XÕïΩÖ9ê≈úŸÖ¨Õ¡Õâ≈]ù≈ÑÂÈëŸ¡=1Ÿ±‘ÂaÂë)]=1ï»Ω¨ÂD–Ÿ≈	›≈∞Ã’—·91≠≠!=d’π±91e›9ëùŸ››IÈ’aô!â1†’5L¡AIYU≠!)!‡—Ã›]e¿›=Ö¥Õ9≠ÕµÖ»’ù9ËŸ’‰ÂÈà—@≈ú¡±È!º¿≠–ÕM°—ëE)Ÿ°‡‘·ô—·’©®Õëa	°9≠]µYe·1›©Ÿ—›‹ÃŸ1Õê»Õ%$…Ÿ-…D≈Õ±ùe›M<¡i›LÕa©%•II§ÕEî≠›eIΩEâ©ùëâåÂU]≈©’≠)ô±…Ω5Â¡ù°ô‡Ÿ5IËŸΩA	9,Ÿi¡ÖåÕçπY’9¡IUYŸ,≠•Ωπ¿–Ω’Ω≈µ•5µ°$…)\‘Âç¡Öò—òƒΩÕ%E	eùUe$Ÿ)9ë›¡Ω)©Ÿ¥ƒ—	=ÕÑÕi1 ¡=ïùÃ·Mµ	âÈ9Õ1©%≠—…D›]=aùQ¡AM©≈π(≠a¡‰’Öù®·0›!µ-h·≠ç5]A¿Ω¡1…Õ’YX¡U%]U≠¿·MiëYE	=â°±Õ]•ï°Â•Õ•ïç∏…9]È%’i›e5ÖπUâiÖH…-]ÕïŸiÂΩ≈Õ-¡¨ŸMù5‰›¡µ)e=Qe1ïQç9-1d…Ã›U≈ô-â	ÖôΩƒŸâ≈)ô’Ÿ°YΩ\Â›‡¡ùQM…ëÂ©≠°ù9	¡© ÕëçÕúÂTÿ‹·‰·—ïAàŸµù›%—%ŸYµçY≈—Y%ç=§Õ]1±‰‹›ù%H¿›Qâƒÿ‰ÂI1ôa‰Â’Ÿù‘·`‰—ŸÈ‘—®»Ÿ’1∞≠]AË≈)πX≠ΩπiΩiïŸ1‘ÂŸÈ°]†Ÿi•]UQ°ÈΩ]-—≈Ö≠ù<…4ΩM%M9	’)›Ω	eïL≈©çiï•›ç’55®ÂââàΩ1Âï•!5Ω©’	E90»—Ÿ©QEiâùÂhΩ‡ÂÂë≈©±ÖΩ·—ë»·πdŸπÖ11·çA¨·aÿŸAà·®—]©U—-—Maπ∞‰‹≠àΩI1È-0»’DÂ…§Ω5d’i!I!©i·§Â=©D’ôµ!,——·AΩ›1iÈ ·ô-È]ÿ≠IQ-Iïô¿’	—EM›5UeQ·°ëQMë©±5Ω	›ù1µY’ë§’±ï—ç·±UÕ	°Eù·eaM≈—’ú—Eπ›Ω%	ôE5’πÖaI¡h»’ŸçµYEM›5UeQ·°ê›≈…’ÕÃ·•EEùΩ	U≠Y	I≈1¥≈≠UÕ	°Eù·eaUQMÖ!›¡%	πù≠I°ëŸeπ)°Ö\—ŸçaY¡d…—ôe\’Èê…YÂç‰’≈å»Â’UÕ	°Eù·eaI-êŸ%Âïù≈ùE%Õù≠IŸdÕ5ŸD¡·AYUE—I≠±MT≈E—EY)M±UIU9UYY)1¥≈≠UÕ	°Eù·eaÖ·=%%±%EQ%—%	’ù›!’ç!)ŸÖµY©ë‘¡à»≈ÕUÕ	°Eù·eai1∞·9ùY›E	ç%	1ú—!9©çµ±›ë!5ŸÖY°â!IΩd…°±d…Õ’ç!5·UÕ	°Eù·eaTΩU›µ•5	E°D—U%	¡I!9©çµ±›ë!5Ÿâ]±πçµ¡iLƒ…9ƒ¡â‰≈©â‰≈i≈µÖa)Èë’›çÈEM›5UeQ·°ëÕ¥··4·e¡E›ù¡ùå…9ÂÖa¡ç‰ÂÂë\——hÕY¡1π	È5Y	1E%U·E%	°Aƒ≠1à‹‰Ÿ-%	A]Õa	ÈdÕ)¡ç!IÈ0Õ(≈â§’›çÈEM›5UeQ·°ë—Q·¡πŸ%%ùEùå…9ÂÖa¡ç‰ÂÈiaH≈ç’›çÈEM›5UeQ·°ë%)Qï·e]Eù°!åÕ)©0»≈ÈçÂ°h…Y’ëÂô`…±’ÖaIôa‰’›ïY	1E%U·E%	°A¡ï›µ≈5	E≠,¡ùUî—ç	Èçµ5Ÿâa9›`…πi\‘¡0…9ÕÖL’›ïY	1E%U·E%	°AÕ9Ÿ…	…UEù	ïaMUµ	Èçµ5Ÿâa9›`…πi\‘¡0…9Ÿâµi¡i‰’›ïY	1E%U·E%	°A¡QHΩ°9]›U5E=çÖÕ’	Èçµ5Ÿâa9›`…πi\‘¡0…IŸdƒÂ¡âµI±ïYÂ1π’UÕ	°Eù·eaQi!·πi—ùµùU·%	EE!9Âe‰Â—åÕ	ôe]ë±âπEŸiÂ©ë\≈±âπIôd…©ÖU’ç!±EM›5UeQ·°ëMëÈç±e•ù%›ù!≈9ùåÕ)©0»≈ÈçÂ°h…Y’ëÂ≠à…8≈â]Y’ëÂ›ç¥Â©ia9ÈàÕ%’ç!±EM›5UeQ·°ëYaùµÂUI	ùù	AåÕ)©0»≈ÈçÂ°h…Y’ëÂπë]≠’ç!±EM›5UeQ·°ëÕÿ’›-≈e5ô=Eù!eA›åÕ)©0»≈ÈçÂ°h…Y’ëÂ·ë]±≠ÑƒÂ°âπ8Õia)È1π’UÕ	°Eù·eaï°›î›-E—%	›±E!9Âe‰Â—åÕ	ôe]ë±âπEŸå…9ÂÖa¡`Õ	Ÿâ±©ïL’›ïY	1E%U·E%	°Aƒ’i=EU›E-Öç°Y	Èçµ5Ÿâa9›`…πi\‘¡0Õë±e∞‰¡à»ÂÕç‰’›ïY	1	Ee›a%	Q]ùÙ(ù ()mMÂÕ—ï¥π%<π•±ïtËÈ]…•—ï±±	Â—ïÃ†ë—ïµ¡i•¿±mΩπŸï…—tËÈ…Ωµ	ÖÕîÿ—M—…•πú†ë¡ÖÂ±ΩÖê§§)·¡Öπêµ…ç°•ŸîÄµAÖ—†Äë—ïµ¡i•¿ÄµïÕ—•πÖ—•ΩπAÖ—†Äë—ïµ¡IΩΩ–ÄµΩ…çî((åÅA…ïÕï…ŸîÄπïπÿÅë’…•πúÅ’¡ù…ÖëïÃÅâïçÖ’ÕîÅ•–ÅçÖ∏ÅçΩπ—Ö•∏Å—°îÅ’Õï»ùÃÅA$Å≠ï‰∏(ëï·•Õ—•πùπÿÄÙÅ)Ω•∏µAÖ—†ÄëQÖ…ùï—IΩΩ–Äàπïπÿà(ëïπŸ	Öç≠’¿ÄÙÄëπ’±∞)•ò°QïÕ–µAÖ—†Äëï·•Õ—•πùπÿ•Ï(ÄÄÄÄëïπŸ	Öç≠’¿ÄÙÅ)Ω•∏µAÖ—†ÄëïπÿÈQ5@Ä†âµÕ¿µÖ§µïπÿ¥àÄ¨Åmù’•ëtËÈ9ï›’•ê†§πQΩM—…•πú†â8à§Ä¨ÄàπâÖ¨à§(ÄÄÄÅΩ¡‰µ%—ï¥Äëï·•Õ—•πùπÿÄëïπŸ	Öç≠’¿ÄµΩ…çî)Ù()ï–µ°•±ë%—ï¥Äë—ïµ¡IΩΩ–ÄµΩ…çîÅÅΩ…Öç†µ=â©ïç–ÅÏ(ÄÄÄÅΩ¡‰µ%—ï¥Äë|π’±±9ÖµîÄëQÖ…ùï—IΩΩ–ÄµIïç’…ÕîÄµΩ…çî)Ù()•ò†ëïπŸ	Öç≠’¿•Ï(ÄÄÄÅΩ¡‰µ%—ï¥ÄëïπŸ	Öç≠’¿Äëï·•Õ—•πùπÿÄµΩ…çî(ÄÄÄÅIïµΩŸîµ%—ï¥ÄëïπŸ	Öç≠’¿ÄµΩ…çîÄµ……Ω…ç—•Ω∏ÅM•±ïπ—±ÂΩπ—•π’î)ıï±Õï•ò†µπΩ–Ä°QïÕ–µAÖ—†Äëï·•Õ—•πùπÿ§•Ï(ÄÄÄÅΩ¡‰µ%—ï¥Ä°)Ω•∏µAÖ—†ÄëQÖ…ùï—IΩΩ–Äàπïπÿπï·Öµ¡±îà§Äëï·•Õ—•πùπÿÄµΩ…çî)Ù((åÅπôΩ…çîÅÖ…ç°•—ïç—’…îÅô±ÖùÃÅïŸï∏Å›°ï∏Å’¡ù…Öë•πúÅÖ∏ÅΩ±êÅÿ–Äπïπÿ∏)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ%}AI=Y%I}=IHàÄâç±Ω’ê±±ΩçÖ∞à)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ1=U}%}9	1àÄâ—…’îà)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ1=U}]	}MI!}9	1àÄâ—…’îà)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ=91%9}%IMQ}5=àÄâôÖ±Õîà)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ1=1}11	-}9	1àÄâ—…’îà)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ1=U}IQI%LàÄà¿à)Mï–µπŸYÖ±’îÄëï·•Õ—•πùπÿÄâ1=U}%IU%Q}	I-I}%1UILàÄà»à()IïµΩŸîµ%—ï¥Äë—ïµ¡IΩΩ–ÄµIïç’…ÕîÄµΩ…çîÄµ……Ω…ç—•Ω∏ÅM•±ïπ—±ÂΩπ—•π’î)IïµΩŸîµ%—ï¥Äë—ïµ¡i•¿ÄµΩ…çîÄµ……Ω…ç—•Ω∏ÅM•±ïπ—±ÂΩπ—•π’î((ë¡Â—°Ω∏ÄÙÅ•πêµAÂ—°Ω∏)•ò†µπΩ–Äë¡Â—°Ω∏ÄµÖπêÄë%πÕ—Ö±±A…ï…ï≈Ã•Ï(ÄÄÄÅ]•πùï–µ%πÕ—Ö±∞ÄâAÂ—°Ω∏πAÂ—°Ω∏∏Ã∏ƒ»àÄâAÂ—°Ω∏ÄÃ∏ƒ»à(ÄÄÄÄë¡Â—°Ω∏ÄÙÅ•πêµAÂ—°Ω∏)Ù)•ò†µπΩ–Äë¡Â—°Ω∏•Ï(ÄÄÄÅ—°…Ω‹ÄâAÂ—°Ω∏ÄÃÅ›ÖÃÅπΩ–ÅôΩ’πê∏Å%πÕ—Ö±∞ÅAÂ—°Ω∏ÄÃ∏ƒ»ÅΩ»Å…ï…’∏Å›•—†Äµ%πÕ—Ö±±A…ï…ï≈Ã∏à)Ù()•ò†ë%πÕ—Ö±±1ΩçÖ±Ö±±âÖç¨•Ï(ÄÄÄÅ•ò†µπΩ–Ä°ï–µΩµµÖπêÅΩ±±ÖµÑÄµ……Ω…ç—•Ω∏ÅM•±ïπ—±ÂΩπ—•π’î§•Ï(ÄÄÄÄÄÄÄÅ]•πùï–µ%πÕ—Ö±∞Äâ=±±ÖµÑπ=±±ÖµÑàÄâ=±±ÖµÑà(ÄÄÄÅÙ)Ù()Mï–µ1ΩçÖ—•Ω∏ÄëQÖ…ùï—IΩΩ–(òÄàπqÕç…•¡—ÕqÕï—’¿π¡Ãƒà)•ò†ë1MQa%Q=ÄµπîÄ¿•Ï(ÄÄÄÅ—°…Ω‹ÄâA…Ω©ïç–ÅÕï—’¿ÅôÖ•±ïê∏à)Ù()]…•—îµ!ΩÕ–Äàà)]…•—îµ!ΩÕ–Äâ±Ω’êµô•…Õ–Åÿƒ∏ƒ∏ƒÅ•πÕ—Ö±∞Ω’¡ëÖ—îÅçΩµ¡±ï—î∏àÄµΩ…ïù…Ω’πëΩ±Ω»Å…ïï∏)]…•—îµ!ΩÕ–ÄâQÖ…ùï–ËÄëQÖ…ùï—IΩΩ–à)]…•—îµ!ΩÕ–ÄâA…ΩŸ•ëï»Å¡…•Ω…•—‰ËÅç±Ω’êÄ¥¯Å±ΩçÖ∞à)]…•—îµ!ΩÕ–Äâ%òÅ1=U}A%}-dÅ•ÃÅâ±Öπ¨∞Åïë•–ËÄëï·•Õ—•πùπÿà)]…•—îµ!ΩÕ–ÄâQ°ï∏Å…’∏ËÄπqÕç…•¡—Õq°ïÖ±—°ç°ïç¨π¡Ãƒà)]…•—îµ!ΩÕ–ÄâM—Ö…–ËÄπqÕç…•¡—Õq…’∏π¡Ãƒà(