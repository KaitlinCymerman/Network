function edit(id) {
    let edit_post = document.querySelector(`#edit-post-${id}`);
    let edit_btn = document.querySelector(`#edit-btn-${id}`);
    edit_post.style.display = 'block';
    edit_btn.style.display = 'block';

    edit_btn.addEventListener('click', () => {
        fetch('/edit/' + id, {
            method: 'PUT',
            body: JSON.stringify({
                post: edit_post.value
            })
          });
          edit_post.style.display = 'none';
          edit_btn.style.display = 'none';
          document.querySelector(`#post-${id}`).innerHTML = edit_post.value;
    });
    edit_post.value = "";
    return false;
}


function like(id) {
    document.querySelector(`#like-button-${id}`).addEventListener('click', () => {
        if (document.querySelector(`#like-button-${id}`).style.backgroundColor == 'white' ) {
            fetch('/like/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    like: true
                })
              })

            document.querySelector(`#like-button-${id}`).style.backgroundColor = 'red';

            fetch('/like/'+ id)
            .then(response => response.json())
            .then(post => {
                document.querySelector(`#like-count-${id}`).innerHTML = post.likes;
            });
        }
        else {
            fetch('/like/' + id, {
                method: 'PUT',
                body: JSON.stringify({
                    like: false
                })
              });

              document.querySelector(`#like-button-${id}`).style.backgroundColor = 'white';

            fetch('/like/'+`${id}`)
            .then(response => response.json())
            .then(post => {
                document.querySelector(`#like-count-${id}`).innerHTML = post.likes;
            });
        }
        return false;
    });
}
