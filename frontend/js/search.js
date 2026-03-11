let lastTarget = null;
function switchTab(name) {
    const currentSection = document.getElementById(`${name}-section`)
    if (lastTarget) {
        lastTarget.style.display = 'none';
    }
    lastTarget = currentSection;
    currentSection.style.display = 'block';
}
function get_icon(fileName) {
    const fileExt = fileName.substring(fileName.lastIndexOf('.'));
    let icon = '📄';
        if (['.js', '.jsx', '.ts', '.tsx'].includes(fileExt)) icon = '📜';
        else if (['.json', '.xml', '.yaml', '.yml'].includes(fileExt)) icon = '📋';
        else if (['.md', '.txt', '.doc', '.docx'].includes(fileExt)) icon = '📝';
        else if (['.png', '.jpg', '.jpeg', '.gif', '.svg'].includes(fileExt)) icon = '🖼️';
        else if (['.py', '.java', '.cpp', '.c'].includes(fileExt)) icon = '💻';
        else if (['.html', '.css'].includes(fileExt)) icon = '🌐';
        else if (['.zip', '.rar', '.7z', '.tar'].includes(fileExt)) icon = '📦';
        else if (['.dll', '.exe', '.app'].includes(fileExt)) icon = '⚙️';
    return icon
}

function render_list(response) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';

    if (!response) {
        resultsList.innerHTML = '<div class="no-results">Please enter a search term, file extension, or substring.</div>';
        return;
    }

    response.forEach((file) => {
        console.log(file)
        const fileName = file.name;
        const fileID = file.id;
        let icon = get_icon(fileName);
        if(file.isdir){
            icon = '📁';
        }
        
        

        // Determine icon based on file extension
        

        const d = document.createElement('div');
        d.className = "result-item";
        d.onclick = () => navigateToParent(fileID, this);
        d.innerHTML = ` <div class="result-icon">${icon}</div>
                            <div class="result-content">
                                <div class="result-filename">${fileName}</div>
                                <div class="result-path"></div>
                            </div>
                            <div class="result-status">✓ Copied</div>`;
        resultsList.appendChild(d);
    });
    
}
async function performSearch() {
    const searchText = document.getElementById('searchText').value;
    const fileExtension = document.getElementById('fileExtension').value;
    const substringSearch = document.getElementById('substringSearch').value;
    const searchFor = document.getElementById('searchFor').value;
    const searchWhere = document.getElementById('searchWhere').value;
    // const output = document.getElementById('output').value;
    // const pythonOutput = document.getElementById('pythonOutput').checked;
    const response = await window.pywebview.api.ultra_search(searchFor, searchWhere, searchText, fileExtension, substringSearch);
    console.log(response);
    render_list(response.data);
    // const resultsList = document.getElementById('resultsList');
    // resultsList.innerHTML = '';

    // if (!response) {
    //     resultsList.innerHTML = '<div class="no-results">Please enter a search term, file extension, or substring.</div>';
    //     return;
    // }

    // response.forEach((file) => {
    //     console.log(file)
    //     const fileName = file.name;
    //     const fileID = file.id;
    //     const icon = get_icon(fileName);
        

    //     // Determine icon based on file extension
        

    //     const d = document.createElement('div');
    //     d.className = "result-item";
    //     d.onclick = () => navigateToID(fileID, this);
    //     d.innerHTML = ` <div class="result-icon">${icon}</div>
    //                         <div class="result-content">
    //                             <div class="result-filename">${fileName}</div>
    //                             <div class="result-path"></div>
    //                         </div>
    //                         <div class="result-status">✓ Copied</div>`;
    //     resultsList.appendChild(d);
    // });
}
// }

async function navigateTo(path, element) {
    await window.pywebview.api.navigate_to(path);

}
async function navigateToID(id, element) {
    await window.pywebview.api.navigate_to_id(id);

}
async function navigateToParent(id, element) {
    await window.pywebview.api.navigate_to_parent(id);

}


async function duplicates() {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    const data = await window.pywebview.api.get_duplicates();
    console.log(data);
    data.forEach(lst => {
        lst.forEach((file) => {
            const fileName = file[1];
            const fileID = file[0];
            const icon = get_icon(fileName);

            const d = document.createElement('div');
            d.className = "result-item";
            d.onclick = () => navigateToParent(fileID, this);

            d.innerHTML = ` <div class="result-icon">${icon}</div>
                            <div class="result-content">
                                <div class="result-filename">${fileName}</div>
                                <div class="result-path"></div>
                            </div>
                            <div class="result-status">✓ Copied</div>`;
            resultsList.appendChild(d);
        })
        const b = document.createElement('div');
        b.className = "seperator";
        resultsList.appendChild(b);
    })

}
async function tagsSearch() {
    const tagsentry = document.getElementById("tagsEntry");
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';

    const response = await window.pywebview.api.tag_search(tagsentry.value);
    if(!response.success){
        alert(response.msg);
    }else{

        render_list(response);
    }
    // console.log(data);
    // data.forEach(file => {

    //     const d = document.createElement('div');
    //     d.className = "result-item";
    //     d.onclick = () => {
    //         navigateTo(`"${file.path}"`, this);
    //     };
    //     d.innerHTML = ` <div class="result-icon">${"icon"}</div>
    //                         <div class="result-content">
    //                             <div class="result-filename">${file.name}</div>
    //                             <div class="result-path">${file.path}</div>
    //                         </div>
    //                         <div class="result-status">✓ Copied</div>`;
    //     resultsList.appendChild(d);

    // })



}

// Allow Enter key to trigger search
document.addEventListener('pywebviewready', async function () {
    document.getElementById('searchText').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    document.getElementById('fileExtension').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    document.getElementById('substringSearch').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    const cwd_field = document.getElementById('cwd-field');
    const cwd_path = await window.pywebview.api.get_cwd();
    cwd_field.innerText = cwd_path;

});
