document.addEventListener('DOMContentLoaded', () => {
    const jobModal = document.getElementById('job-modal');
    const progressModal = document.getElementById('progress-modal');
    const loadingModal = document.getElementById('loading-modal');
    const quoteModal = document.getElementById('quote-modal');
    const usageGraphContainer = document.getElementById('usage-graph');
    const modalTimelineContainer = document.getElementById('timeline');
    const dateSelector = document.getElementById('date-selector');

    let currentJobData = {};
    let selectedDate = new Date();
    let selectedSlots = [];
    const reservations = {};

    // --- INITIALIZATION ---
    function init() {
        // Init dummy reservation data
        for (let i = 0; i < 7; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            const dateString = date.toISOString().split('T')[0];
            reservations[dateString] = new Set();
            const numReservations = Math.floor(Math.random() * 20) + 10;
            for (let j = 0; j < numReservations; j++) {
                reservations[dateString].add(Math.floor(Math.random() * 48));
            }
        }
        
        setupEventListeners();
        generateDates();
        generateDashboardTimeline();
        generateModalTimeline();
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        // Header profile
        const userProfile = document.getElementById('user-profile');
        const dropdownMenu = document.getElementById('dropdown-menu');
        userProfile.addEventListener('click', () => {
            dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
        });
        document.addEventListener('click', (e) => {
            if (!userProfile.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });

        // Modals
        document.getElementById('open-modal-btn').addEventListener('click', () => jobModal.style.display = 'flex');
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => e.target.closest('.modal-container').style.display = 'none');
        });
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-container')) {
                e.target.style.display = 'none';
            }
        });

        // Dynamic inputs in submission modal
        document.getElementById('job-type-select').addEventListener('change', (e) => {
            document.querySelectorAll('.type-input').forEach(div => div.style.display = 'none');
            if (e.target.value) {
                document.getElementById(`${e.target.value}-inputs`).style.display = 'block';
            }
        });

        // Submission flow
        document.getElementById('request-quote-btn').addEventListener('click', handleQuoteRequest);
        document.getElementById('cancel-quote-btn').addEventListener('click', () => quoteModal.style.display = 'none');
        document.getElementById('confirm-quote-btn').addEventListener('click', handleQuoteConfirmation);
        
        // Job queue click
        document.querySelector('#job-table tbody').addEventListener('click', handleJobRowClick);
    }
    
    // --- TIMELINE GENERATION ---
    function createTimelineGrid(container, isInteractive) {
        container.innerHTML = '';
        container.classList.toggle('interactive', isInteractive);
        
        for (let hour = 0; hour < 24; hour += 4) { // Create labels for 0, 4, 8, 12, 16, 20
            const label = document.createElement('div');
            label.classList.add('hour-label');
            label.textContent = `${String(hour).padStart(2, '0')}:00`;
            label.style.gridRow = (hour / 4) + 1;
            container.appendChild(label);
            
            const slotRow = document.createElement('div');
            slotRow.classList.add('slots-row');
            slotRow.style.gridRow = (hour / 4) + 1;
            
            for (let i = 0; i < 8; i++) { // 4 hours * 2 slots
                const slotIndex = hour * 2 + i;
                const slot = document.createElement('div');
                slot.classList.add('time-slot');
                slot.dataset.slotIndex = slotIndex;
                slotRow.appendChild(slot);
            }
            container.appendChild(slotRow);
        }
    }
    
    function populateTimeline(container, date, isInteractive) {
        const dateString = date.toISOString().split('T')[0];
        const dailyReservations = reservations[dateString] || new Set();

        container.querySelectorAll('.time-slot').forEach(slot => {
            const slotIndex = parseInt(slot.dataset.slotIndex, 10);
            
            // Reset classes
            slot.className = 'time-slot';
            
            if (dailyReservations.has(slotIndex)) {
                slot.classList.add('reserved');
            } else {
                slot.classList.add('available');
                if (isInteractive) {
                    if (selectedSlots.includes(slotIndex)) {
                        slot.classList.add('selected');
                    }
                    slot.onclick = () => {
                        if (slot.classList.contains('selected')) {
                            slot.classList.remove('selected');
                            selectedSlots = selectedSlots.filter(s => s !== slotIndex);
                        } else {
                            slot.classList.add('selected');
                            selectedSlots.push(slotIndex);
                        }
                        selectedSlots.sort((a, b) => a - b);
                    };
                }
            }
        });
    }

    function generateDashboardTimeline() {
        createTimelineGrid(usageGraphContainer, false);
        populateTimeline(usageGraphContainer, new Date(), false);
    }

    function generateModalTimeline() {
        createTimelineGrid(modalTimelineContainer, true);
        populateTimeline(modalTimelineContainer, selectedDate, true);
    }

    function generateDates() {
        dateSelector.innerHTML = '';
        for (let i = 0; i < 7; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            const btn = document.createElement('button');
            btn.classList.add('date-btn');
            if (i === 0) btn.classList.add('active');
            btn.textContent = `${date.getMonth() + 1}/${date.getDate()}`;
            btn.dataset.date = date.toISOString().split('T')[0];
            btn.addEventListener('click', () => {
                selectedDate = new Date(btn.dataset.date + 'T00:00:00');
                document.querySelector('.date-btn.active').classList.remove('active');
                btn.classList.add('active');
                selectedSlots = [];
                generateModalTimeline();
            });
            dateSelector.appendChild(btn);
        }
    }

    // --- HANDLER FUNCTIONS ---
    function handleQuoteRequest() {
        const jobName = document.getElementById('job-name-input').value.trim();
        const jobType = document.getElementById('job-type-select').value;
        if (jobName === '' || jobType === '' || selectedSlots.length === 0) {
            alert('작업 이름, 유형, 예약 시간을 모두 선택해주세요.');
            return;
        }
        
        currentJobData = {
            name: jobName, type: jobType,
            urgency: document.getElementById('job-urgency-select').value, slots: selectedSlots
        };
        jobModal.style.display = 'none';
        loadingModal.style.display = 'flex';

        setTimeout(() => {
            loadingModal.style.display = 'none';
            const typeSelect = document.getElementById('job-type-select');
            const typeText = typeSelect.options[typeSelect.selectedIndex].text;
            const urgencyMap = {low: "낮음", medium: "보통", high: "높음"};
            const urgencyText = urgencyMap[currentJobData.urgency];

            document.getElementById('quote-job-type').textContent = typeText;
            document.getElementById('quote-urgency').textContent = urgencyText;
            document.getElementById('quote-summary').textContent = `${currentJobData.name} (${typeText})`;
            document.getElementById('quote-priority-reason').textContent = `${urgencyText} 긴급도로 요청되어, 유사 등급 작업과 경합 후 배정됩니다.`;
            document.getElementById('quote-cost').textContent = `약 ${currentJobData.slots.length * 1500}원`;
            
            const startSlot = currentJobData.slots[0];
            const startTime = `${String(Math.floor(startSlot / 2)).padStart(2, '0')}:${String((startSlot % 2) * 30).padStart(2, '0')}`;
            document.getElementById('quote-time').textContent = `${selectedDate.toLocaleDateString()} ${startTime} 부터`;

            quoteModal.style.display = 'flex';
        }, 1000);
    }

    function handleQuoteConfirmation() {
        const startSlot = currentJobData.slots[0];
        const endSlot = currentJobData.slots[currentJobData.slots.length - 1];
        const startTime = `${String(Math.floor(startSlot / 2)).padStart(2, '0')}:${String((startSlot % 2) * 30).padStart(2, '0')}`;
        const endTime = `${String(Math.floor((endSlot + 1) / 2)).padStart(2, '0')}:${String(((endSlot + 1) % 2) * 30).padStart(2, '0')}`;
        
        const newRow = document.querySelector('#job-table tbody').insertRow(0);
        newRow.innerHTML = `
            <td>#${Math.floor(Math.random() * 1000) + 2044}</td>
            <td>${currentJobData.name}</td>
            <td>한준교</td>
            <td class="status-waiting">대기중</td>
            <td>${startTime}</td>
            <td>${endTime}</td>
        `;
        newRow.dataset.status = 'Waiting';
        newRow.dataset.reason = 'AI 견적 승인 후 제출됨';
        newRow.dataset.queuePosition = '마지막';
        newRow.dataset.waitTime = '미정';
        
        const dateString = selectedDate.toISOString().split('T')[0];
        currentJobData.slots.forEach(slotIndex => reservations[dateString].add(slotIndex));
        
        generateDashboardTimeline(); // Refresh dashboard timeline
        generateModalTimeline(); // Refresh modal timeline
        
        quoteModal.style.display = 'none';
        alert('작업이 성공적으로 제출되었습니다.');
    }

    function handleJobRowClick(e) {
        const row = e.target.closest('tr');
        if (!row) return;

        const status = row.dataset.status;
        const title = document.getElementById('progress-modal-title');
        const body = document.getElementById('progress-modal-body');
        
        title.textContent = `[${row.cells[1].textContent}] 작업 진행 상태`;

        if (status === 'Running') {
            const progress = row.dataset.progress;
            const endTime = row.dataset.endTime;
            body.innerHTML = `<p>현재 작업이 <strong>${progress}%</strong> 완료되었습니다.</p><div class="progress-bar-container"><div class="progress-bar" style="width: ${progress}%;">${progress}%</div></div><p>예상 종료 시간: <strong>${endTime}</strong></p>`;
        } else if (status === 'Waiting') {
            const reason = row.dataset.reason;
            const position = row.dataset.queuePosition;
            const waitTime = row.dataset.waitTime;
            body.innerHTML = `<p><strong>${reason}</strong>(으)로 인해 <strong>${position}</strong>번째 순서에 실행이 배정되었습니다.</p><p>약 <strong>${waitTime}</strong>분 후에 실행될 예정입니다.</p>`;
        } else if (status === 'Failed') {
            const failReason = row.dataset.failReason;
            body.innerHTML = `<p>작업이 다음 이유로 실패했습니다:</p><p><strong>${failReason}</strong></p><button>재시도</button>`;
        }
        progressModal.style.display = 'flex';
    }

    // --- RUN APP ---
    init();
});