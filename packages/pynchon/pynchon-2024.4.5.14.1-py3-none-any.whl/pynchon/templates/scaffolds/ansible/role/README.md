# {{name}}

An ansible role that sets up ...

# Role Variables

See [defaults/main.yml](defaults/main.yml) for an up to date list.

# Requirements / Dependencies

See [requirements.yml](examples/requirements.yml) and [requirements.txt](examples/requirements.txt)

# Example Playbook

```
- name: all
  hosts: local
  become: yes
  become_method: sudo
  gather_facts: no
  pre_tasks: []
  vars: {}
  roles:
    # user config: bash aliases, inputrc, etc
    - name: {{name}}
  tasks: []
```

## License

MIT