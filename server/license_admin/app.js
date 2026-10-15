'use strict';
let bearer = '';
const el = id => document.getElementById(id);
async function request(path, method = 'GET', body) {
    const response = await fetch(path, {method, credentials:'omit', cache:'no-store',
        headers: {'Content-Type':'application/json', ...(bearer ? {Authorization:'Bearer '+bearer} : {})},
        ...(body ? {body: JSON.stringify(body)} : {})});
    const value = await response.json();
    if (!response.ok) { if (response.status === 401) clear(); throw new Error(value.detail || 'Falha na operação.'); }
    return value;
}
function clear() { bearer=''; el('panel').hidden=true; el('login').hidden=false; el('keys').textContent=''; el('users').textContent=''; el('audit').textContent=''; el('subscriptions').replaceChildren(); }
async function safely(work) { try { await work(); el('message').textContent='Operação concluída.'; } catch(error) { el('message').textContent=error.message; } }
async function refresh() {
    el('users').replaceChildren();
    for (const user of await request('/admin/users')) {
        const item=document.createElement('div'); const text=document.createElement('span');
        text.textContent=user.id+' | '+user.name+' | '+user.email+' '; item.append(text);
        const edit=document.createElement('button'); edit.textContent='Corrigir cadastro';
        edit.onclick=()=>safely(async()=> { const name=prompt('Nome corrigido',user.name); if(!name)return; const email=prompt('E-mail corrigido',user.email); if(!email)return; await request('/admin/users/'+user.id,'PUT',{name,email}); await refresh(); });
        item.append(edit); el('users').append(item);
    }
    el('audit').textContent=JSON.stringify(await request('/admin/audit'),null,2);
    const rows=await request('/admin/subscriptions'); el('subscriptions').replaceChildren();
    for (const row of rows) {
        const card=document.createElement('article'); const text=document.createElement('pre');
        text.textContent=JSON.stringify(row,null,2); card.append(text);
        const action=(label, path, body) => { const button=document.createElement('button'); button.textContent=label; button.onclick=()=>safely(async()=> { if (!confirm(label+'?')) return; const result=await request(path,'POST',body); if(result.key) el('keys').textContent=JSON.stringify(result,null,2); await refresh(); }); card.append(button); };
        for (const [label, operation] of [['Renovar','renew'],['Suspender','suspend'],['Retomar','resume'],['Revogar definitivamente','revoke']]) action(label,'/admin/subscriptions/'+row.id,{action:operation});
        action('Renovar como mensal','/admin/subscriptions/'+row.id,{action:'renew',plan:'monthly'});
        action('Renovar como anual','/admin/subscriptions/'+row.id,{action:'renew',plan:'annual'});
        for (const device of row.devices) { action('Substituir vaga '+device.slot,'/admin/subscriptions/'+row.id+'/slots/'+device.slot+'/replace',{}); if(device.activation_id) action('Revogar computador '+device.slot,'/admin/activations/'+device.activation_id+'/revoke',{}); }
        el('subscriptions').append(card);
    }
}
el('login').onsubmit=event=>{ event.preventDefault(); safely(async()=>{ const data=Object.fromEntries(new FormData(event.target)); const value=await request('/admin/login','POST',data); event.target.reset(); bearer=value.access_token; el('login').hidden=true; el('panel').hidden=false; await refresh(); }); };
el('user').onsubmit=event=>{ event.preventDefault(); safely(async()=>{ await request('/admin/users','POST',Object.fromEntries(new FormData(event.target))); event.target.reset(); await refresh(); }); };
el('subscription').onsubmit=event=>{ event.preventDefault(); safely(async()=>{ el('keys').textContent=JSON.stringify(await request('/admin/subscriptions','POST',Object.fromEntries(new FormData(event.target))),null,2); await refresh(); }); };
el('refresh').onclick=()=>safely(refresh);
el('logout').onclick=()=>safely(async()=>{try { await request('/admin/logout','POST',{}); } finally { clear(); }});
window.addEventListener('pagehide',clear);
