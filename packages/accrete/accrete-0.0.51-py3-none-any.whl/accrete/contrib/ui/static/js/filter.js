document.body.addEventListener('htmx:afterSwap', function(evt) {
    checkSelectedFields();
});
window.addEventListener('click', showHide);
buildQueryTagsFromUrl();
resetInput();
checkSelectedFields();

function buildQueryTagsFromUrl() {
    const queryTags = document.getElementById('query-tags');
    removeQueryTagsChildren();
    const queryGroup = createQueryGroup();
    queryTags.appendChild(queryGroup)
    buildQueryFromQueryString(normalizeQueryString(), queryGroup, '&');
    toggleFilterModalButton();
}

function removeQueryTagsChildren() {
    const queryTags = document.getElementById('query-tags');
    while (queryTags.firstElementChild) {
        queryTags.firstElementChild.remove();
    }
}

function buildQueryFromQueryString(jsonQuery, queryGroup, operator='&') {
    for (let item of jsonQuery) {
        if (isString(item)) {
            operator = item
        }
        else if (isObject(item)) {
            operator = queryGroup.firstElementChild && operator || null;
            for (let term in item) {
                queryGroup.appendChild(createQueryTag(term, operator, item[term]));
                operator = '&';
            }
        }
        else if (isArray(item)) {
            const subQueryGroup = createQueryGroup(
                queryGroup.firstElementChild && operator || null
            );
            queryGroup.appendChild(createOperatorSelect(operator));
            queryGroup.appendChild(subQueryGroup);
            buildQueryFromQueryString(item, subQueryGroup, operator);
        }
    }
}

function queryStringFromJsonQuery() {
    return JSON.stringify(buildJsonQueryFromHtml())
}

function buildJsonQueryFromHtml(tagGroup=null) {
    const queryTags = (
        tagGroup || document.getElementById('query-tags').firstElementChild);
    let query = []
    if (!queryTags) {
        return query
    }
    for (let tag of queryTags.children) {
        if (tag.classList.contains('query-tag-operator')) {
            const operator = tag.firstElementChild.value
            if (operator !== '&') {query.push(operator);}
        }
        else if (tag.classList.contains('query-group-operator')) {
            const operator = tag.firstElementChild.firstElementChild.value;
            if (operator !== '&') {query.push(operator);}
        }
        else if (tag.classList.contains('query-group')) {
            query.push(buildJsonQueryFromHtml(tag))
        }
        else if (tag.classList.contains('query-tag-container')) {
            if (tag.firstElementChild.classList.contains('query-tag-operator')) {
                const operator = tag.firstElementChild.firstElementChild.value
                if (operator !== '&') {query.push(operator);}
            }
            if (tag.lastElementChild.classList.contains('query-tag')) {
                const key = tag.lastElementChild.getAttribute(
                    'data-param'
                );
                let value = tag.lastElementChild.getAttribute(
                    'data-value'
                );
                if (typeof value === 'string') {
                    if (value.toLowerCase() === 'true') {
                        value = true
                    }
                    else if (value.toLowerCase() === 'false') {
                        value = false
                    }
                }
                query.push({[key]: value})
            }
        }
    }
    return query
}

function setQueryParam(queryParam) {
    const queryLabel = getCompleteQueryText(queryParam);
    const queryNotificationLabel = document.getElementById('query-label');
    queryNotificationLabel.innerText = queryLabel;
    setInputType(queryParam);
}

function setInputType(queryParam) {
    const queryInput = document.getElementById('query-input');
    const query = queryParam.getAttribute('id');
    const dataType = queryParam.getAttribute('data-type');
    const queryLabel = getCompleteQueryText(queryParam);
    const step = queryParam.getAttribute('data-step') || null;
    const inputControl = document.getElementById('query-input-control');
    const selectControl = document.getElementById('query-input-select-control');
    queryInput.setAttribute('data-param', query);
    queryInput.setAttribute('data-text', queryLabel);
    if (dataType === 'selection') {
        const selectInput = document.getElementById('query-input-select');
        const options = queryParam.querySelector('.param-options');
        selectInput.innerHTML = options.innerHTML
        selectControl.classList.remove('is-hidden');
        inputControl.classList.add('is-hidden');
        selectInput.setAttribute('data-param', query);
        selectInput.setAttribute('data-text', queryLabel);
        return
    }
    selectControl.classList.add('is-hidden');
    inputControl.classList.remove('is-hidden');
    queryInput.setAttribute('type', dataType);
    if (step) {queryInput.step = step;}
    queryInput.select()
}

function inputConfirm() {
    if (this.event.key === 'Enter') {
        applyInput();
    }
}

function applyInput() {
    const input = getActiveInput();
    if (!input.reportValidity()) {
        return
    }
    const edit = document.querySelector('.selected-query-edit');
    const tag = document.querySelector('.selected-query-tag');
    let group = (
        document.querySelector('.selected-query-group')
        || document.getElementById('query-tags').firstElementChild
    );
    if (!group) {
        group = document.getElementById('query-tags').appendChild(createQueryGroup());
    }
    if (edit) {
        editQueryTag(edit.closest('.query-tag-container'));
    }
    else if (tag) {
        const container = tag.closest('.query-tag-container');
        const previous = container.previousElementSibling;
        if (previous) {
            appendToTag(container);
        }
        else {
            appendAfterTag(container);
        }
    }
    else {
        const operator = (
            group.childElementCount
            && document.getElementById('query-operation-select').value
            || null
        );
        group.appendChild(createQueryTag(
            input.getAttribute('data-param'),
            operator,
            input.value
        ));
    }
    fetchQuery();
    resetInput();
    input.scrollIntoView();
}

function editQueryTag(queryTagContainer) {
    const input = getActiveInput();
    const param = input.getAttribute('data-param');
    const operator = (
        queryTagContainer.previousElementSibling
        && document.getElementById('query-operation-select').value
        || null
    );
    const queryTag = createQueryTag(param, operator, input.value);
    queryTagContainer.replaceWith(queryTag);
}

function appendToTag(queryTagContainer) {
    const input = getActiveInput();
    const operator = (
        queryTagContainer.firstElementChild.classList.contains('query-tag-operator')
        && queryTagContainer.firstElementChild.firstElementChild.value
        || '&'
    );
    const operatorSelect = createOperatorSelect(operator);
    const queryGroup = createQueryGroup();
    queryTagContainer.after(operatorSelect);
    if (queryTagContainer.firstElementChild.classList.contains('query-tag-operator')) {
        queryTagContainer.firstElementChild.remove();
    }
    operatorSelect.after(queryGroup);

    queryGroup.appendChild(queryTagContainer);
    queryGroup.appendChild(createQueryTag(
        input.getAttribute('data-param'),
        document.getElementById('query-operation-select').value,
        input.value)
    );

}

function appendAfterTag(queryTagContainer) {
    const input = getActiveInput();
    const operator = document.getElementById('query-operation-select').value;
    const tag = createQueryTag(
        input.getAttribute('data-param'), operator, input.value
    );
    queryTagContainer.after(tag);
}

function resetInput() {
    const input = document.getElementById('query-input');
    const queryParam = getParamElement(input.getAttribute('data-default-term'))
    if (!queryParam) {
        return
    }
    const queryLabel = getCompleteQueryText(queryParam);
    const queryNotificationLabel = document.getElementById('query-label');
    queryNotificationLabel.innerText = queryLabel;
    setInputType(queryParam);
    const queryInput = getActiveInput();
    queryInput.value = null;
}

function fetchQuery(queryString=null) {
    const queryApply = document.getElementById('query-apply');
    const queryApplyEvent = new Event('click');
    const url = new URL(window.location)
    url.searchParams.set('q', queryString ?? queryStringFromJsonQuery());
    queryApply.setAttribute('hx-get', url.toString());
    htmx.process(queryApply);
    queryApply.dispatchEvent(queryApplyEvent);
    toggleFilterModalButton();
}

function toggleFilterModalButton() {
    const button = document.getElementById('modal-filter-button');
    const query = document.getElementById('query-tags');
    if (query.firstElementChild && query.firstElementChild.childElementCount) {
        button.classList.add('is-active');
    }
    else {
        button.classList.remove('is-active');
    }
}

function checkSelectedFields() {
    const table = document.getElementById('content-table');
    if (!table) {
        return
    }
    const header = table.querySelectorAll('th')
    document.getElementById(
        'field-path-checkboxes'
    ).querySelectorAll(
        'input:checked'
    ).forEach((el) => {el.checked = ''});
    header.forEach((th) => {
        const name = th.getAttribute('data-name');
        if (name) {
            document.getElementById(
                'field-path-checkboxes'
            ).querySelector(`input[name=${name}]`
            ).checked = 'checked';
        }
    })
}

//-----------------------------------------------------------------------------
// Events
//-----------------------------------------------------------------------------

function showHide() {
    const target = this.event.target;
    const queryInput = document.getElementById('query-input-fieldset');
    if (!queryInput) {
        return;
    }
    const queryParamDropDown = document.getElementById('query-params-dropdown');
    const operation = document.getElementById('query-operation');
    if (queryInput.contains(target)
        || queryParamDropDown.contains(target)
        || operation.contains(target)
    ) {
        queryParamDropDown.classList.remove('is-hidden');
        return
    }
    queryParamDropDown.classList.add('is-hidden');
}

function showFilterModal() {
    const filterModal = document.getElementById('filter-modal');
    const modalContent = document.getElementById('modal-content');
    modalContent.appendChild(document.getElementById('query-block'));
    filterModal.classList.add('is-active');
}

function hideFilterModal() {
    const filterModal = document.getElementById('filter-modal');
    const panel = document.getElementById('filter-panel');
    panel.appendChild(document.getElementById('query-block'));
    filterModal.classList.remove('is-active');
}

function toggleParams() {
    const target = this.event.target
    const nextSibling = target.nextElementSibling;
    if (!nextSibling) {
        return
    }
    if (nextSibling.classList.contains('query-params')) {
        nextSibling.classList.toggle('is-hidden');
    }
    if (nextSibling.classList.contains('param-options')) {
        setQueryParam(nextSibling.parentElement);
    }
}

function deleteQueryTag(event) {
    const tagContainer = event.currentTarget.closest('.query-tag-container');
    const previousTagContainer = tagContainer.previousElementSibling;
    const nextTagContainer = tagContainer.nextElementSibling;
    const queryGroup = tagContainer.parentElement;

    if (
        previousTagContainer
        && nextTagContainer
        && tagContainer.firstElementChild.classList.contains('query-tag-operator')
    ) {
        if (nextTagContainer.childElementCount === 1) {
            nextTagContainer.prepend(tagContainer.firstElementChild)
        }
    }
    tagContainer.remove();
    if (
        !previousTagContainer
        && nextTagContainer
        && nextTagContainer.firstElementChild.classList.contains('query-tag-operator')
    ) {
        nextTagContainer.firstElementChild.remove();
    }
    if (!queryGroup.childElementCount) {
        queryGroup.previousElementSibling && queryGroup.previousElementSibling.remove();
        queryGroup.remove();
    }
    else if (
        queryGroup.firstElementChild
        && queryGroup.firstElementChild.classList.contains('query-group-operator')
    ) {
        if (!isFirstQueryGroup(queryGroup)) {
            queryGroup.previousElementSibling && queryGroup.previousElementSibling.remove();
            while (queryGroup.childElementCount) {
                queryGroup.after(queryGroup.lastElementChild);
            }
            queryGroup.remove();
        }
        else {
            queryGroup.firstElementChild.remove();
            const subQueryGroup = queryGroup.firstElementChild;
            while (subQueryGroup.childElementCount) {
                subQueryGroup.before(subQueryGroup.firstElementChild);
            }
            subQueryGroup.remove();
        }
    }
    fetchQuery();
}

function setSelectedTag(event) {
    event.stopPropagation();
    const toDeactivate = event.currentTarget.classList.contains(
        'selected-query-tag'
    );
    unselectAll();
    if (!toDeactivate) {
        event.currentTarget.classList.add('selected-query-tag');
    }
}

function setSelectedQueryGroup(event) {
    event.stopPropagation();
    const toDeactivate = event.currentTarget.classList.contains(
        'selected-query-group-selector'
    );
    unselectAll();
    if (!toDeactivate) {
        event.currentTarget.classList.add('selected-query-group-selector');
        const parent = event.currentTarget.closest('.query-group-operator');
        parent.nextElementSibling.classList.add('selected-query-group');
    }
}

function selectForEdit(event) {
    event.stopPropagation();
    const toDeactivate = event.currentTarget.classList.contains(
        'selected-query-edit'
    );
    unselectAll();
    if (toDeactivate) {
        return
    }
    const tag = event.currentTarget.closest('.query-tag');
    event.currentTarget.classList.add('selected-query-edit');
    setQueryParam(getParamElement(
        tag.getAttribute('data-param'),
        tag.getAttribute('data-value')
    ));
    const input = getActiveInput();
    input.value = tag.getAttribute('data-value')
    if (input.type === 'select-one') {
        return;
    }
    input.select()
}

function unselectAll() {
    unselectAllQueryGroups();
    unselectAllQueryTags();
    unselectAllQueryEdits();
}

function unselectAllQueryTags() {
    document.querySelectorAll('.selected-query-tag').forEach(
        (tag) => {
            tag.classList.remove('selected-query-tag')
        }
    );
}

function unselectAllQueryGroups() {
    document.querySelectorAll(
        '.selected-query-group, .selected-query-group-selector'
    ).forEach(
        (tag) => {
            tag.classList.remove(
                'selected-query-group', 'selected-query-group-selector'
            )
        }
    );
}

function unselectAllQueryEdits() {
    document.querySelectorAll('.selected-query-edit').forEach(
        (tag) => {tag.classList.remove('selected-query-edit')}
    );
}

function changeOperator(event) {
    fetchQuery();
}

function filterFieldPaths() {
    const value = document.getElementById('field-path-search-input').value.toString().toLowerCase();
    const checkBoxes = document.getElementById('field-path-checkboxes');
    if (!value) {
        checkBoxes.querySelectorAll(':scope * input').forEach(
            (el) => {
                el.parentElement.classList.remove('is-hidden')
            });
        return
    }
    const pathsToShow = checkBoxes.querySelectorAll(`:scope * input[data-label*=${value}]`);
    const pathsToHide = checkBoxes.querySelectorAll(`:scope * input:not([data-label*=${value}])`);
    pathsToShow.forEach((el) => {el.parentElement.classList.remove('is-hidden')});
    pathsToHide.forEach((el) => {el.parentElement.classList.add('is-hidden')})
}

function changeFieldSelection() {
    const fieldPathApply = document.getElementById('field-path-apply');
    const fieldPathApplyEvent = new Event('click');
    const url = new URL(window.location);
    const fieldPaths = document.getElementById('field-path-checkboxes');
    const selected = fieldPaths.querySelectorAll('input:checked');
    let fields = [];
    selected.forEach((input) => {
        fields.push(input.name);
    })
    url.searchParams.set('fields', JSON.stringify(fields));
    fieldPathApply.setAttribute('hx-get', url.toString());
    htmx.process(fieldPathApply);
    fieldPathApply.dispatchEvent(fieldPathApplyEvent);
}

function resetFieldPaths() {
    const fieldPathApply = document.getElementById('field-path-apply');
    const fieldPathApplyEvent = new Event('click');
    const url = new URL(window.location)
    url.searchParams.delete('fields');
    fieldPathApply.setAttribute('hx-get', url.toString());
    htmx.process(fieldPathApply);
    fieldPathApply.dispatchEvent(fieldPathApplyEvent);
}

//-----------------------------------------------------------------------------
// Elements
//-----------------------------------------------------------------------------

function createQueryGroup(operator=null) {
    const queryGroup = document.createElement('div');
    queryGroup.classList.add('query-group');
    return queryGroup
}

function createQueryTag(term, operator, value=null) {
    let displayValue;
    const element = getParamElement(term, value);
    const dataType = element.getAttribute('data-type');
    const text = getCompleteQueryText(element);
    if (dataType === 'selection') {
        const option = element.querySelector(
            `.param-options > option[value="${value}"]`
        );
        displayValue = option.textContent;
    }
    else {
        displayValue = value;
    }
    return createTag(text, term, value, displayValue, operator);
}

function createTag(text, param, value, displayValue, operator) {
    const tagContainer = document.createElement('div');
    const tag = document.createElement('div');
    const tagEditDiv = document.createElement('div');
    const tagEditIcon = document.createElement('div');
    const tagText = document.createElement('span');
    const tagDeleteDiv = document.createElement('div');
    const tagDeleteButton = document.createElement('button');
    tagEditDiv.classList.add('query-tag-edit')
    tagEditDiv.addEventListener('click', selectForEdit);
    tagEditDiv.appendChild(tagEditIcon);
    tagEditIcon.classList.add('icon-edit', 'query-tag-edit-icon');
    tagText.classList.add('query-tag-text', 'is-size-7', 'is-unselectable');
    tagText.innerText = text.concat(displayValue && `: ${displayValue}` || '');
    tagDeleteDiv.classList.add('query-tag-delete')
    tagDeleteButton.classList.add('delete', 'mx-1');
    tagDeleteDiv.appendChild(tagDeleteButton);
    tagDeleteButton.addEventListener('click', deleteQueryTag);
    tag.addEventListener('click', setSelectedTag);
    tag.classList.add('query-tag');
    tag.tabIndex = -1;
    tag.setAttribute('data-param', param.replace('filter-id-', ''));
    tag.setAttribute('data-value', value);
    tag.appendChild(tagEditDiv);
    tag.appendChild(tagText);
    tag.appendChild(tagDeleteDiv);
    if (operator && operator !== '&') {
        tagContainer.appendChild(createOperatorDiv(operator));
    }
    tagContainer.appendChild(tag);
    tagContainer.classList.add('query-tag-container');
    return tagContainer
}

function createOperatorDiv(operator) {
    const operatorContainer = document.createElement('div');
    const operatorDiv = document.createElement('div');
    operatorContainer.classList.add('query-tag-operator');
    operatorDiv.innerText = getOperatorLabel(operator);
    operatorDiv.value = operator;
    operatorDiv.setAttribute('value', operator);
    operatorContainer.appendChild(operatorDiv);
    return operatorContainer
}

function createOperatorSelect(operator) {
    const selectContainer = document.createElement('div');
    const selectDiv = document.createElement('div');
    const select = document.createElement('select');
    const andOption = document.createElement('option');
    const orOption = document.createElement('option');
    const xorOption = document.createElement('option');
    const groupSelectorDiv = document.createElement('div');
    const groupSelector = document.createElement('button');
    groupSelectorDiv.classList.add('query-group-selector');
    groupSelector.classList.add('icon-select');
    groupSelectorDiv.appendChild(groupSelector);
    andOption.value = '&';
    andOption.innerText = getOperatorLabel('&');
    orOption.innerText = getOperatorLabel('|');
    xorOption.innerText = getOperatorLabel('^');
    orOption.value = '|';
    xorOption.value = '^';
    if (operator === '&') {andOption.setAttribute('selected', '')}
    else if (operator === '|') {orOption.setAttribute('selected', '')}
    else if (operator === '^') {xorOption.setAttribute('selected', '')}
    select.appendChild(andOption);
    select.appendChild(orOption);
    select.addEventListener('change', changeOperator);
    selectDiv.classList.add('select')
    selectDiv.appendChild(select);
    if (operator === '^') {select.appendChild(xorOption);}
    selectContainer.classList.add(
        'query-group-operator', 'is-size-7', 'mr-1', 'mb-1'
    );
    selectContainer.appendChild(selectDiv);
    selectContainer.appendChild(groupSelectorDiv);
    groupSelector.addEventListener('click', setSelectedQueryGroup);
    return selectContainer
}

//-----------------------------------------------------------------------------
// Helper
//-----------------------------------------------------------------------------

function normalizeQueryString(queryString=null, left=null) {
    queryString = queryString || JSON.parse(
        new URL(window.location.href).searchParams.get('q') || '[]'
    );
    let normalizedQueryString = []
    for (let item of queryString) {
        if (isString(item)) {
            normalizedQueryString.push(item)
            left = item
        }
        else if (isObject(item)) {
            for (let k in item) {
                if (left && !isString(left)) {
                    normalizedQueryString.push('&')
                }
                normalizedQueryString.push({[k]: item[k]})
                left = item
            }
        }
        else if (isArray(item)) {
            if (left && !isString(left)) {
                normalizedQueryString.push('&')
            }
            normalizedQueryString.push(normalizeQueryString(item))
            left = item
        }
    }
    return normalizedQueryString
}

function getOperatorLabel(operator) {
    const queryTags = document.getElementById('query-tags');
    if (operator === '&') {
        return queryTags.getAttribute('data-and-label')
    }
    else if (operator === '|') {
        return queryTags.getAttribute('data-or-label')
    }
    else if (operator === '^') {
        return queryTags.getAttribute('data-xor-label')
    }
}

function getParamElement(param, value=null){
    const filterId = `filter-id-${param.replace('filter-id-', '')}`
    return document.getElementById(filterId)
}

function getCompleteQueryText(paramElement) {
    let names = getQueryTextParts(paramElement);
    return names.join(' \u2192 ')
}

function getQueryTextParts(paramElement) {
    let currentElement = paramElement;
    let names = [];
    names.push(currentElement.firstElementChild.innerText);
    while (currentElement.parentElement.parentElement.classList.contains('query-param')) {
        currentElement = currentElement.parentElement.parentElement;
        names.push(currentElement.firstElementChild.innerText);
    }
    return names.reverse()
}

function getActiveInput() {
    const input = document.getElementById('query-input');
    return (
        input.parentElement.classList.contains('is-hidden')
        && document.getElementById('query-input-select')
        || input
    )
}

function isObject(item) {
    return Object.prototype.toString.apply(item) === '[object Object]'
}


function isArray(item) {
    return Object.prototype.toString.apply(item) === '[object Array]'
}


function isString(item) {
    return Object.prototype.toString.apply(item) === '[object String]'
}

function isFirstQueryGroup(queryGroup) {
    return queryGroup.parentElement.id === 'query-tags'
}
