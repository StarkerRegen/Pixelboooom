let postList = [];
$('.img-thumbnail').click(function(e) {
    let img = document.getElementById(this.id);
    if(!confirmEnding(img.src,'background.png')) {
        let name = img.classList;
        let postForm = document.getElementById('postform');
        let id = this.id + 'm'
        let input = document.getElementById('img');
        if(name.length == 1) {
            img.style.border = "4px solid #111";
            img.classList.add('selected');
            postList.push(this.id);
            let img_m = document.createElement('img');
            img_m.src = img.src;
            img_m.setAttribute('id',id);
            postForm.appendChild(img_m);
        }else {
            img.style.border = "0";
            img.classList.remove('selected');
            postList.pop(this.id);
            document.getElementById(id).remove();
        }
        input.value = postList.toString();
        document.getElementById('style').value = this.parentNode.id;
    }
});

$('#submit').click(function(e) {
    $('#postcard').modal('hide');
});

$('#postcard').on('show.bs.modal', function () {
    document.getElementById('title').value = '';
    document.getElementById('category').value = '';
});

function confirmEnding(str, target) {
    var start = str.length-target.length;
    var arr = str.substr(start,target.length);
    if(arr == target){
        return true;
    }
    return false;
}