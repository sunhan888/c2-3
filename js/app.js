const form = document.querySelector('#idea-form');
const gradeInput = document.querySelector('#grade');
const interestInput = document.querySelector('#interest');
const topicInput = document.querySelector('#topic');
const submitButton = document.querySelector('#submit-button');
const message = document.querySelector('#form-message');
const resultSection = document.querySelector('#idea-result');
const retryButton = document.querySelector('#retry-button');

const REQUEST_TIMEOUT_MS = 20000;

function setMessage(text = '', type = 'error') {
  message.textContent = text;
  message.classList.toggle('is-info', type === 'info');
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.querySelector('.button-label').textContent = isLoading
    ? '아이디어를 다듬는 중…'
    : '아이디어 만들기';
  submitButton.querySelector('.button-spark').textContent = isLoading ? '⋯' : '✦';
}

function validateForm() {
  const values = {
    grade: gradeInput.value.trim(),
    interest: interestInput.value.trim(),
    topic: topicInput.value.trim(),
  };

  if (!values.grade || !values.interest || !values.topic) {
    setMessage('학년, 관심사, 주제를 모두 입력해 주세요.');
    const firstEmpty = !values.grade ? gradeInput : !values.interest ? interestInput : topicInput;
    firstEmpty.focus();
    return null;
  }

  return values;
}

function createListItem(text) {
  const item = document.createElement('li');
  item.textContent = text;
  return item;
}

function renderIdea(idea) {
  document.querySelector('#result-title').textContent = idea.title;
  document.querySelector('#result-tagline').textContent = idea.tagline;
  document.querySelector('#result-summary').textContent = idea.summary;
  document.querySelector('#result-tip').textContent = idea.tip;

  const steps = document.querySelector('#result-steps');
  steps.replaceChildren(...idea.steps.map(createListItem));

  resultSection.hidden = false;
  window.setTimeout(() => {
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 80);
}

function getFriendlyError(response, payload) {
  if (response.status === 400) return payload?.error || '입력 내용을 다시 확인해 주세요.';
  if (response.status === 429) return '요청이 많아요. 잠시 후 다시 시도해 주세요.';
  if (response.status >= 500) return payload?.error || 'AI가 잠시 생각을 정리하고 있어요. 잠시 후 다시 시도해 주세요.';
  return payload?.error || '아이디어를 만드는 중 문제가 생겼어요. 다시 시도해 주세요.';
}

async function requestIdea(values) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch('/api/generate_idea', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
      signal: controller.signal,
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(getFriendlyError(response, payload));
    if (!payload.idea) throw new Error('아이디어 결과를 읽지 못했어요. 한 번 더 시도해 주세요.');
    return payload.idea;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('응답이 늦어지고 있어요. 네트워크를 확인한 뒤 다시 시도해 주세요.');
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const values = validateForm();
  if (!values) return;

  setMessage('AI가 당신의 재료를 아이디어로 바꾸고 있어요.', 'info');
  setLoading(true);

  try {
    const idea = await requestIdea(values);
    setMessage('');
    renderIdea(idea);
  } catch (error) {
    setMessage(error.message || '아이디어를 만드는 중 문제가 생겼어요. 다시 시도해 주세요.');
  } finally {
    setLoading(false);
  }
});

retryButton.addEventListener('click', () => {
  resultSection.hidden = true;
  setMessage('다른 관심사나 주제로 다시 만들어 보세요.', 'info');
  document.querySelector('#generator').scrollIntoView({ behavior: 'smooth', block: 'start' });
  interestInput.focus();
});
