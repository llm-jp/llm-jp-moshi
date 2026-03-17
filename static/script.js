const videoDir = 'static/video/';
const audioDir = 'static/audio/';
const textDir = 'static/text/';


// Generate Interactive Demo Videos
$(document).ready(function () {
    const videoFiles = [
        ["20260130/llmjp-moshi-demo1.mp4", "20260222/demo-1.mp4"],
        ["20260224/demo-2.mp4", "20260222/demo-4.mp4"],
    ];
    videoFiles.forEach(([file1, file2]) => {
        const videoElement = `
            <div class="row mb-4">
                <div class="col-12 col-md-6 mb-4 mb-md-0">
                    <div class="ratio ratio-8x5">
                        <video class="object-fit-contain" controls>
                            <source src="${videoDir + file1}" type="video/mp4">
                            Your browser does not support HTML video.
                        </video>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <div class="ratio ratio-8x5">
                        <video class="object-fit-contain" controls>
                            <source src="${videoDir + file2}" type="video/mp4">
                            Your browser does not support HTML video.
                        </video>
                    </div>
                </div>
            </div>
        `;
        $('#demo-video-container').append(videoElement);
    });
});


// Generate Dialogue Continuation Table
$(document).ready(function () {
    const columns = {
        'Prompt': [],
        'Generation': ['Re-synthesis', 'J-Moshi', 'LLM-jp-Moshi-v1'],
    };
    const promptFiles = [
        '20260130/Prompt/23.wav',
        '20260130/Prompt/39.wav',
        '20260130/Prompt/15.wav',
        '20260130/Prompt/14.wav',
        '20260130/Prompt/18.wav',
    ];
    const generationFiles = [
        ['20260130/Resynth/23.wav', '20260130/J-Moshi/23.wav', '20260130/LLM-jp-Moshi-v1/23.wav'],
        ['20260130/Resynth/39.wav', '20260130/J-Moshi/39.wav', '20260130/LLM-jp-Moshi-v1/39.wav'],
        ['20260130/Resynth/15.wav', '20260130/J-Moshi/15.wav', '20260130/LLM-jp-Moshi-v1/15.wav'],
        ['20260130/Resynth/14.wav', '20260130/J-Moshi/14.wav', '20260130/LLM-jp-Moshi-v1/14.wav'],
        ['20260130/Resynth/18.wav', '20260130/J-Moshi/18.wav', '20260130/LLM-jp-Moshi-v1/18.wav'],
    ];
    const table = $('#continuation-table')

    // Add header
    // first header: Prompt (colspan=1, rowspan=2) + Generation (colspan=3, rowspan=1)
    // second header: Re-synthesis + J-Moshi-v2 (step-9282) + J-Moshi-v2 (step-13041)
    const thead = $('<thead>');
    const headerRow1 = $('<tr>');
    headerRow1.append($('<th>', { colspan: 1, rowspan: 2 }).text('Prompt'));
    headerRow1.append($('<th>', { colspan: 3 }).text('Generation'));
    thead.append(headerRow1);
    const headerRow2 = $('<tr>');
    columns['Generation'].forEach(header => {
        headerRow2.append($('<th>').text(header));
    });
    thead.append(headerRow2);
    table.append(thead);

    // Add rows
    const tbody = $('<tbody>');
    promptFiles.forEach((prompt, i) => {
        const row = $('<tr>');
        const promptCell = $('<td>');
        const promptAudio = $('<audio controls>').append(
            $('<source>', { src: audioDir + prompt, type: 'audio/wav' })
        );
        promptCell.append(promptAudio);
        row.append(promptCell);
        generationFiles[i].forEach((generation, j) => {
            const cell = $('<td>');
            const audio = $(`<audio id="audio-${i}-${j}" controls>`)
            cell.append(audio);
            row.append(cell);
        });
        tbody.append(row);
    });
    table.append(tbody);
    promptFiles.forEach((prompt, i) => {
        generationFiles[i].forEach((generation, j) => {
            mergeAudioWithBell(
                audioDir + prompt, audioDir + generation, audioDir + "bell.mp3", 0.1
            ).then(audioURL => {
                $(`#audio-${i}-${j}`).append($('<source>', { src: audioURL, type: 'audio/wav' }));
            });
        });
    });
});


// Generate Multi-stream TTS Table
// Text data loader
function loadTextData(filename) {
    return new Promise((resolve, reject) => {
        $.get(textDir + filename, data => {
            resolve(data);
        });
    });
};

$(document).ready(function () {
    const columns = ['Text', 'Synthesized Audio'];
    const files = [
        ['daily-1-0679.txt', 'daily-1-0679.wav'],
        ['daily-1-0823.txt', 'daily-1-0823.wav'],
        ['daily-4-0373.txt', 'daily-4-0373.wav'],
        ['daily-5-0276.txt', 'daily-5-0276.wav'],
        ['daily-5-0726.txt', 'daily-5-0726.wav'],
    ];
    const table = $('#mstts-table');

    // Add header
    const thead = $('<thead>');
    const headerRow = $('<tr>');
    columns.forEach(header => {
        headerRow.append($('<th>').text(header));
    });
    thead.append(headerRow);
    table.append(thead);

    // Add rows
    const tbody = $('<tbody>');
    files.forEach((file, i) => {
        const row = $('<tr>');
        // Add text cell ("text-align: left;min-width: 200px;")
        const textCell = $('<td>').css('text-align', 'left');//.css('min-width', '100px');
        const textPromise = loadTextData(file[0]);
        textPromise.then(text => {
            textCell.text(text);
        });
        row.append(textCell);
        // Add waveform cell
        const waveCell = $('<td>');//.css('min-width', '200px');
        const waveform = $('<div>').attr('id', `waveform-${i}`);
        waveCell.append(waveform);
        const playPauseButton = `
            <button class="btn btn-secondary" data-action="play" id="play-pause-${i}">
                <i class="bi bi-play-fill"></i> Play / <i class="bi bi-pause-fill"></i> Pause
            </button>
        `;
        waveCell.append(playPauseButton);
        row.append(waveCell);
        tbody.append(row);
    });
    table.append(tbody);

    // Create wavesurfer instances
    files.forEach((file, i) => {
        const wavesurfer = WaveSurfer.create({
            container: `#waveform-${i}`,
            url: audioDir + file[1],
            splitChannels: [
                {
                    waveColor: '#2E7D9E',
                    progressColor: '#173E4E',
                },
                {
                    waveColor: '#E57872',
                    progressColor: '#2A0908',
                }
            ],
            barWidth: 2,
            height: 55,
            responsive: true,
        });
        $(`#play-pause-${i}`).click(() => {
            wavesurfer.playPause();
        });
    });
});


// Dataset switching functionality
$(document).ready(function () {
    $('.dataset-btn').click(function () {
        const dataset = $(this).data('dataset');

        // Update button states
        $('.dataset-btn').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');

        // Show/hide dataset content
        $('.dataset-content').hide();
        $(`#dataset-${dataset}`).show();
    });
});


// Hide language switcher on scroll
$(document).ready(function () {
    const langSwitch = $('.lang-switch');
    let scrollThreshold = 50;

    $(window).scroll(function () {
        if ($(this).scrollTop() > scrollThreshold) {
            langSwitch.addClass('hidden');
        } else {
            langSwitch.removeClass('hidden');
        }
    });
});


// Language switching functionality
$(document).ready(function () {
    // Get default language
    const urlParams = new URLSearchParams(window.location.search);
    // Validate lang parameter
    const validLangs = ['ja', 'en'];
    if (!urlParams.has('lang') || !validLangs.includes(urlParams.get('lang'))) {
        console.warn(`Invalid or missing 'lang' parameter. Defaulting to 'ja'.`);
        // Remove invalid lang parameter from URL
        const newUrl = window.location.href.split('?')[0];
        window.history.replaceState({}, document.title, newUrl);
        // Set default language to Japanese
        defaultLang = 'ja';
    } else {
        defaultLang = urlParams.get('lang');
    }

    // Set initial language
    switchLanguage(defaultLang);
    localStorage.setItem('selectedLanguage', defaultLang);

    // Language button click handler
    $('.lang-btn').click(function () {
        const lang = $(this).data('lang');
        switchLanguage(lang);
        localStorage.setItem('selectedLanguage', lang);
    });

    function switchLanguage(lang) {
        // Update button states
        console.log(`Switching to language: ${lang}`);
        $('.lang-btn').removeClass('btn-primary').addClass('btn-outline-primary');
        $(`.lang-btn[data-lang="${lang}"]`).removeClass('btn-outline-primary').addClass('btn-primary');

        // Show/hide language-specific content
        $('[lang]').removeClass('active-lang');
        $(`[lang="${lang}"]`).addClass('active-lang');
    }
});
